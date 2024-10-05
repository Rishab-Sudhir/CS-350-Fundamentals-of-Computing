/*******************************************************************************
* Dual-Threaded FIFO Server Implementation w/ Queue Limit
*
* Description:
*     A server implementation designed to process client requests in First In,
*     First Out (FIFO) order. The server binds to the specified port number
*     provided as a parameter upon launch. It launches a secondary thread to
*     process incoming requests and allows to specify a maximum queue size.
*
* Usage:
*     <build directory>/server -q <queue_size> <port_number>
*
* Parameters:
*     port_number - The port number to bind the server to.
*     queue_size  - The maximum number of queued requests
*
* Author:
*     Renato Mancuso
*
* Affiliation:
*     Boston University
*
* Creation Date:
*     September 29, 2023
*
* Last Update:
*     September 25, 2024
*
* Notes:
*     Ensure to have proper permissions and available port before running the
*     server. The server relies on a FIFO mechanism to handle requests, thus
*     guaranteeing the order of processing. If the queue is full at the time a
*     new request is received, the request is rejected with a negative ack.
*
*******************************************************************************/

#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sched.h>
#include <signal.h>

/* Needed for wait(...) */
#include <sys/types.h>
#include <sys/wait.h>

/* Needed for semaphores */
#include <semaphore.h>

/* Include struct definitions and other libraries that need to be
 * included by both client and server */
#include "common.h"

#define BACKLOG_COUNT 100
#define USAGE_STRING				\
	"Missing parameter. Exiting.\n"		\
	"Usage: %s -q <queue size> <port_number>\n"

#include <unistd.h>  // For getopt()
#include <pthread.h>  // Include for pthread functions


/* START - Variables needed to protect the shared queue. DO NOT TOUCH */
sem_t * queue_mutex;
sem_t * queue_notify;
/* END - Variables needed to protect the shared queue. DO NOT TOUCH */

struct server_request {
	struct request req; // the original request from the client
	struct timespec receipt_timestamp; // Timestamp when the server recieved the request
};

struct queue {
	struct server_request *items; // Dynamic array to hold server request items
	int front;
	int rear;
	int count; // Number of items currently in the queue
	int capacity; // Max capacity of the queue
};


struct worker_params {
	// Same as HW2
    struct queue *the_queue;		// Pointer to the shared queue
	int conn_socket;				// Connection socket to communicate with the client
	volatile int *terminate_flag;	// Pointer to the termination flag - volatile so its tracked everytime it changes

};

/* Helper function to perform queue initialization */
void queue_init(struct queue * the_queue, size_t queue_size)
{
	the_queue->items = (struct server_request *)malloc(queue_size * sizeof(struct server_request));
	if (the_queue->items == NULL){
		perror("Failed to allocate memory for queue items");
		exit(EXIT_FAILURE);
	}
	the_queue->front = 0;
	the_queue->rear = 0;
	the_queue->count = 0;
	the_queue->capacity = queue_size;
}

/* Implement this method to correctly dump the status of the queue
 * following the format Q:[R<request ID>,R<request ID>,...] */
void dump_queue_status(struct queue * the_queue)
{
	int i;
	/* QUEUE PROTECTION INTRO START --- DO NOT TOUCH */
	sem_wait(queue_mutex);
	/* QUEUE PROTECTION INTRO END --- DO NOT TOUCH */

	/* WRITE YOUR CODE HERE! */
	/* MAKE SURE NOT TO RETURN WITHOUT GOING THROUGH THE OUTRO CODE! */
	// Same as HW2
	printf("Q:[");
	for (i = 0; i < the_queue->count;i++) {
		int index = (the_queue->front + i) % the_queue->capacity;
		printf("R%ld", the_queue->items[index].req.req_id);
		if (i < the_queue->count - 1){
			printf(",");
		}
	}
	printf("]\n");

	/* QUEUE PROTECTION OUTRO START --- DO NOT TOUCH */
	sem_post(queue_mutex);
	/* QUEUE PROTECTION OUTRO END --- DO NOT TOUCH */
}

/* Add a new request <request> to the shared queue <the_queue> */
int add_to_queue(struct server_request to_add, struct queue * the_queue)
{
	int retval = 0;
	/* QUEUE PROTECTION INTRO START --- DO NOT TOUCH */
	sem_wait(queue_mutex);
	/* QUEUE PROTECTION INTRO END --- DO NOT TOUCH */

	/* WRITE YOUR CODE HERE! */
	/* MAKE SURE NOT TO RETURN WITHOUT GOING THROUGH THE OUTRO CODE! */

	/* Make sure that the queue is not full */
	if (the_queue->count == the_queue->capacity) {
		// Queue is full, handle the rejection
		retval= -1; // Indicate rejection

	} else {
		/* If all good, add the item in the queue */
		/* IMPLEMENT ME !!*/
		// Same as HW2 except for queue size
		// Add the request to the rear of the queue
		the_queue->items[the_queue->rear] = to_add;
		// update the rear index
		the_queue->rear = (the_queue->rear + 1) % the_queue->capacity;
		// Increment the count of items in the queue
		the_queue->count++;

		/* QUEUE SIGNALING FOR CONSUMER --- DO NOT TOUCH */
		sem_post(queue_notify);

		retval = 0; // Success
	}

	/* QUEUE PROTECTION OUTRO START --- DO NOT TOUCH */
	sem_post(queue_mutex);
	/* QUEUE PROTECTION OUTRO END --- DO NOT TOUCH */
	return retval;
}

struct server_request get_from_queue(struct queue * the_queue)
{
    struct server_request retval;
    /* QUEUE PROTECTION INTRO START --- DO NOT TOUCH */
    sem_wait(queue_notify);
    sem_wait(queue_mutex);
    /* QUEUE PROTECTION INTRO END --- DO NOT TOUCH */

	/* Check if the queue is empty */
    if (the_queue->count == 0) {
        /* Return a special value to indicate an empty queue */
        retval.req.req_id = -1; // Use -1 as a sentinel value
    } else {
		/* Retrieve the request from the front of the queue */
		retval = the_queue->items[the_queue->front];
		the_queue->front = (the_queue->front + 1) % the_queue->capacity;
		the_queue->count--;
	}

    /* QUEUE PROTECTION OUTRO START --- DO NOT TOUCH */
    sem_post(queue_mutex);
    /* QUEUE PROTECTION OUTRO END --- DO NOT TOUCH */
    return retval;
}

/* Main logic of the worker thread */
/* IMPLEMENT HERE THE MAIN FUNCTION OF THE WORKER */
void *worker_main(void *arg){

	// Cast the arguement to the appropriate type
	struct worker_params *params = (struct worker_params *)arg;

	// Extract Parameters
	struct queue *the_queue = params->the_queue;
	int conn_socket = params->conn_socket;
	volatile int *terminate = params->terminate_flag; // declare as volatile

	// Loop until termination flag is set
	while (1) {

		// Acquire queue_mutex to check the_queue->count safely
        sem_wait(queue_mutex);
        int queue_is_empty = (the_queue->count == 0);
        sem_post(queue_mutex);

        // Check if termination flag is set and queue is empty
        if (*terminate && queue_is_empty) {
			//printf("Worker: Termination flag set and queue is empty. Exiting.\n");
            break; // Exit the loop and terminate the thread
        }

		// Get the next server_request from the queue
        struct server_request sreq = get_from_queue(the_queue);

		// Check if the queue was empty and termination is requested
        if (sreq.req.req_id == -1) {
            // No more requests, exit the loop
            break;
        }

        struct request req = sreq.req;
        struct timespec receipt_timestamp = sreq.receipt_timestamp;

		// Record the start timestamp
		struct timespec start_time;
		clock_gettime(CLOCK_MONOTONIC, &start_time);

		// Process the request (basically simulating busy wait)
		busywait_timespec(req.req_length);

		// Record the completion timestamp
		struct timespec completion_time;
		clock_gettime(CLOCK_MONOTONIC, &completion_time);

		// Send the response back to the client
		struct response resp;
		resp.req_id = req.req_id;
		resp.ack = 0; // Indicate Acceptance
		send(conn_socket, &resp, sizeof(struct response), 0);

		// Print the required information
        printf("R%ld:%lf,%lf,%lf,%lf,%lf\n",
               req.req_id,
               TSPEC_TO_DOUBLE(req.req_timestamp),
               TSPEC_TO_DOUBLE(req.req_length),
               TSPEC_TO_DOUBLE(receipt_timestamp),
               TSPEC_TO_DOUBLE(start_time),
               TSPEC_TO_DOUBLE(completion_time));

        // Dump the queue status
        dump_queue_status(the_queue);
	}

	// Exit the thread
	return NULL;
}


/* Main function to handle connection with the client. This function
 * takes in input conn_socket and returns only when the connection
 * with the client is interrupted. */
void handle_connection(int conn_socket, int queue_size)
{
	struct request * req;
	struct queue * the_queue;
	size_t in_bytes;

	volatile int terminate_flag = 0; // declare as volatile
	pthread_t worker_thread;
	struct worker_params *params;

	/* The connection with the client is alive here. Let's
	 * initialize the shared queue. */
	/* IMPLEMENT HERE ANY QUEUE INITIALIZATION LOGIC */

	// Create and initialize the queue
	the_queue = (struct queue *)malloc(sizeof(struct queue));
	if (the_queue == NULL) {
		perror("Failed to initialize queue");
		shutdown(conn_socket, SHUT_RDWR); // Added shutdown
		close(conn_socket);
		return;
	}

	queue_init(the_queue, queue_size);
	

	/* Queue ready to go here. Let's start the worker thread. */

	/* IMPLEMENT HERE THE LOGIC TO START THE WORKER THREAD. */

	// Initialize the worker parameters
	params = (struct worker_params *)malloc(sizeof(struct worker_params));
	if (params == NULL) {
		perror("Failed to allocate memory for the worker params");
		free(the_queue);
		shutdown(conn_socket, SHUT_RDWR); // Added shutdown
		close(conn_socket);
		return;
	}
	params->the_queue = the_queue;
	params->conn_socket = conn_socket;
	params->terminate_flag = &terminate_flag;

	// Start the worker thread
	if (pthread_create(&worker_thread, NULL, worker_main, (void *)params) != 0) {
		perror("Failed to create worker thread");
		free(the_queue);
		free(params);
		shutdown(conn_socket, SHUT_RDWR); // Added shutdown
		close(conn_socket);
		return;
	}

	/* We are ready to proceed with the rest of the request
	 * handling logic. */

	/* REUSE LOGIC FROM HW1 TO HANDLE THE PACKETS */

	req = (struct request *)malloc(sizeof(struct request));
	if (req == NULL) {
		perror("Failed to allocate memory for request");
		terminate_flag = 1;
		sem_post(queue_notify);
		pthread_join(worker_thread, NULL);
		free(the_queue);
		free(params);
		shutdown(conn_socket, SHUT_RDWR); // Added shutdown
		close(conn_socket);
		return;
	}

	/* Don't just return if in_bytes is 0 or -1. Instead
		* skip the response and break out of the loop in an
		* orderly fashion so that we can de-allocate the req
		* and resp varaibles, and shutdown the socket. */
	do {
		in_bytes = recv(conn_socket, req, sizeof(struct request),0);
		if (in_bytes > 0) {

			// Record the receipt timestamp
			struct timespec receipt_timestamp;
			clock_gettime(CLOCK_MONOTONIC, &receipt_timestamp);

			struct server_request sreq;
			sreq.req = *req;
			sreq.receipt_timestamp = receipt_timestamp;

			// Add the request to the queue
			int retval = add_to_queue(sreq, the_queue);

			if (retval == -1) {
				// request was rejected
				// Record the reject timestamp
				struct timespec reject_timestamp;
				clock_gettime(CLOCK_MONOTONIC, &reject_timestamp);

				// Send the rejection response to the client
				struct response resp;
				resp.req_id = sreq.req.req_id;
				resp.ack = 1; // Indicate rejection
				send(conn_socket, &resp, sizeof(struct response), 0);

				// Print the rejection log
				printf("X%ld:%lf,%lf,%lf\n",
					sreq.req.req_id,
					TSPEC_TO_DOUBLE(sreq.req.req_timestamp),
					TSPEC_TO_DOUBLE(sreq.req.req_length),
					TSPEC_TO_DOUBLE(reject_timestamp)
					);
				
				// Dump queue statut
				dump_queue_status(the_queue);
			}
		} else if (in_bytes == 0) {
			// Client has closed connection
			printf("INFO: CLient disconnected. \n");
			break;
		} else {
			perror("Error recieving data");
			break;
		}
		}  while (in_bytes > 0);

	/* PERFORM ORDERLY DEALLOCATION AND OUTRO HERE */
	
	
	/* Ask the worker thead to terminate */
	/* ASSERT TERMINATION FLAG FOR THE WORKER THREAD */
	sem_wait(queue_mutex);
    terminate_flag = 1;
    sem_post(queue_mutex);
	/* Make sure to wake-up any thread left stuck waiting for items in the queue. DO NOT TOUCH */
	sem_post(queue_notify);
	/* Wait for orderly termination of the worker thread */	
	/* ADD HERE LOGIC TO WAIT FOR TERMINATION OF WORKER */
	pthread_join(worker_thread, NULL);
	/* FREE UP DATA STRUCTURES AND SHUTDOWN CONNECTION WITH CLIENT */

	free(req);
	free(the_queue);
	free(params);

	shutdown(conn_socket, SHUT_RDWR);
	close(conn_socket);
}


/* Template implementation of the main function for the FIFO
 * server. The server must accept in input a command line parameter
 * with the <port number> to bind the server to. */
int main (int argc, char ** argv) {
	int sockfd, retval, accepted, optval;
	in_port_t socket_port;
	struct sockaddr_in addr, client;
	struct in_addr any_address;
	socklen_t client_len;

	/* Parse all the command line arguments */
	/* PARSE THE COMMANDS LINE: */
	/* 1. Detect the -q parameter and set aside the queue size  */

	int queue_size = 0; // default will set after parsing

	/*Parse all the command line arugments*/
	int opt;
	while ((opt = getopt(argc, argv, "q:")) != -1) {
		switch(opt){
			case 'q':
				queue_size = atoi(optarg);
				if (queue_size <= 0) {
					fprintf(stderr, "Invalid queue size specified.\n");
					fprintf(stderr, USAGE_STRING, argv[0]);
					exit(EXIT_FAILURE);
				}
				break;
			default:
				fprintf(stderr, USAGE_STRING, argv[0]);
				exit(EXIT_FAILURE);
		}
	}
	
	/* 2. Detect the port number to bind the server socket to (see HW1 and HW2) */

	if (optind >= argc) {
		fprintf(stderr, "Invalid port number after queue size.\n");
		fprintf(stderr, USAGE_STRING, argv[0]);
		exit(EXIT_FAILURE);
	}

	socket_port = strtol(argv[optind], NULL, 10);
	printf("INFO: setting server port as: %d\n", socket_port);
    printf("INFO: setting queue size as: %d\n", queue_size);

	/* Now onward to create the right type of socket */
	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	if (sockfd < 0) {
		ERROR_INFO();
		perror("Unable to create socket");
		return EXIT_FAILURE;
	}

	/* Before moving forward, set socket to reuse address */
	optval = 1;
	setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (void *)&optval, sizeof(optval));

	/* Convert INADDR_ANY into network byte order */
	any_address.s_addr = htonl(INADDR_ANY);

	/* Time to bind the socket to the right port  */
	addr.sin_family = AF_INET;
	addr.sin_port = htons(socket_port);
	addr.sin_addr = any_address;

	/* Attempt to bind the socket with the given parameters */
	retval = bind(sockfd, (struct sockaddr *)&addr, sizeof(struct sockaddr_in));

	if (retval < 0) {
		ERROR_INFO();
		perror("Unable to bind socket");
		return EXIT_FAILURE;
	}

	/* Let us now proceed to set the server to listen on the selected port */
	retval = listen(sockfd, BACKLOG_COUNT);

	if (retval < 0) {
		ERROR_INFO();
		perror("Unable to listen on socket");
		return EXIT_FAILURE;
	}

	/* Ready to accept connections! */
	printf("INFO: Waiting for incoming connection...\n");
	client_len = sizeof(struct sockaddr_in);
	accepted = accept(sockfd, (struct sockaddr *)&client, &client_len);

	if (accepted == -1) {
		ERROR_INFO();
		perror("Unable to accept connections");
		return EXIT_FAILURE;
	}

	/* Initialize queue protection variables. DO NOT TOUCH. */
	queue_mutex = (sem_t *)malloc(sizeof(sem_t));
	queue_notify = (sem_t *)malloc(sizeof(sem_t));
	retval = sem_init(queue_mutex, 0, 1);
	if (retval < 0) {
		ERROR_INFO();
		perror("Unable to initialize queue mutex");
		return EXIT_FAILURE;
	}
	retval = sem_init(queue_notify, 0, 0);
	if (retval < 0) {
		ERROR_INFO();
		perror("Unable to initialize queue notify");
		return EXIT_FAILURE;
	}
	/* DONE - Initialize queue protection variables. DO NOT TOUCH */

	/* Ready to handle the new connection with the client. */
	handle_connection(accepted, queue_size);

	free(queue_mutex);
	free(queue_notify);

	close(sockfd);
	return EXIT_SUCCESS;

}