/*******************************************************************************
* Single-Threaded FIFO Image Server Implementation w/ Queue Limit
*
* Description:
*     A server implementation designed to process client
*     requests for image processing in First In, First Out (FIFO)
*     order. The server binds to the specified port number provided as
*     a parameter upon launch. It launches a secondary thread to
*     process incoming requests and allows to specify a maximum queue
*     size.
*
* Usage:
*     <build directory>/server -q <queue_size> -w <workers> -p <policy> <port_number>
*
* Parameters:
*     port_number - The port number to bind the server to.
*     queue_size  - The maximum number of queued requests.
*     workers     - The number of parallel threads to process requests.
*     policy      - The queue policy to use for request dispatching.
*
* Author:
*     Renato Mancuso
*
* Affiliation:
*     Boston University
*
* Creation Date:
*     October 31, 2023
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
#include <pthread.h>

/* Needed for wait(...) */
#include <sys/types.h>
#include <sys/wait.h>

/* Needed for semaphores */
#include <semaphore.h>

#include <inttypes.h> // For PRIu64 format 

/* Include struct definitions and other libraries that need to be
 * included by both client and server */
#include "common.h"

struct image * image_array[1024]; // stores pointers to images indexed by img_id

#define BACKLOG_COUNT 100
#define USAGE_STRING				\
	"Missing parameter. Exiting.\n"		\
	"Usage: %s -q <queue size> "		\
	"-w <workers: 1> "			\
	"-p <policy: FIFO> "			\
	"<port_number>\n"

/* 4KB of stack for the worker thread */
#define STACK_SIZE (4096)

/* Mutex needed to protect the threaded printf. DO NOT TOUCH */
sem_t * printf_mutex;

/* Synchronized printf for multi-threaded operation */
#define sync_printf(...)			\
	do {					\
		sem_wait(printf_mutex);		\
		printf(__VA_ARGS__);		\
		sem_post(printf_mutex);		\
	} while (0)

/* START - Variables needed to protect the shared queue. DO NOT TOUCH */
sem_t * queue_mutex;
sem_t * queue_notify;
/* END - Variables needed to protect the shared queue. DO NOT TOUCH */

struct request_meta {
	struct request request;
	struct timespec receipt_timestamp;
	struct timespec start_timestamp;
	struct timespec completion_timestamp;
};

enum queue_policy {
	QUEUE_FIFO,
	QUEUE_SJN
};

struct queue {
	size_t wr_pos;
	size_t rd_pos;
	size_t max_size;
	size_t available;
	int number_of_items; // new field to track items (tracks size of queue)
	enum queue_policy policy;
	struct request_meta * requests;
};

struct connection_params {
	size_t queue_size;
	size_t workers;
	enum queue_policy queue_policy;
};

struct worker_params {
	int conn_socket;
	int worker_done;
	struct queue * the_queue;
	int worker_id;
};

enum worker_command {
	WORKERS_START,
	WORKERS_STOP
};


void queue_init(struct queue * the_queue, size_t queue_size, enum queue_policy policy)
{
	the_queue->rd_pos = 0;
	the_queue->wr_pos = 0;
	the_queue->max_size = queue_size;
	the_queue->requests = (struct request_meta *)malloc(sizeof(struct request_meta)
						     * the_queue->max_size);
	the_queue->available = queue_size;
	the_queue->policy = policy;
	the_queue->number_of_items = 0; // initialize the number of items
}

/* Add a new request <request> to the shared queue <the_queue> */
int add_to_queue(struct request_meta to_add, struct queue * the_queue)
{
	int retval = 0;
	/* QUEUE PROTECTION INTRO START --- DO NOT TOUCH */
	sem_wait(queue_mutex);
	/* QUEUE PROTECTION INTRO END --- DO NOT TOUCH */

	/* WRITE YOUR CODE HERE! */
	/* MAKE SURE NOT TO RETURN WITHOUT GOING THROUGH THE OUTRO CODE! */

	/* Make sure that the queue is not full */
	if (the_queue->available == 0) {
		retval = 1;
	} else {
		/* If all good, add the item in the queue */
		the_queue->requests[the_queue->wr_pos] = to_add;
		the_queue->wr_pos = (the_queue->wr_pos + 1) % the_queue->max_size;
		the_queue->available--;
		the_queue->number_of_items++; // increment the number of items
		/* QUEUE SIGNALING FOR CONSUMER --- DO NOT TOUCH */
		sem_post(queue_notify);
	}

	/* QUEUE PROTECTION OUTRO START --- DO NOT TOUCH */
	sem_post(queue_mutex);
	/* QUEUE PROTECTION OUTRO END --- DO NOT TOUCH */
	return retval;
}

/* Add a new request <request> to the shared queue <the_queue> */
struct request_meta get_from_queue(struct queue * the_queue)
{
	struct request_meta retval;
	/* QUEUE PROTECTION INTRO START --- DO NOT TOUCH */
	sem_wait(queue_notify);
	sem_wait(queue_mutex);
	/* QUEUE PROTECTION INTRO END --- DO NOT TOUCH */

	/* WRITE YOUR CODE HERE! */
	/* MAKE SURE NOT TO RETURN WITHOUT GOING THROUGH THE OUTRO CODE! */
	retval = the_queue->requests[the_queue->rd_pos];
	the_queue->rd_pos = (the_queue->rd_pos + 1) % the_queue->max_size;
	the_queue->available++;
	the_queue->number_of_items--; //decrement the number of items

	/* QUEUE PROTECTION OUTRO START --- DO NOT TOUCH */
	sem_post(queue_mutex);
	/* QUEUE PROTECTION OUTRO END --- DO NOT TOUCH */
	return retval;
}

void dump_queue_status(struct queue * the_queue)
{
	size_t i, j;
	/* QUEUE PROTECTION INTRO START --- DO NOT TOUCH */
	sem_wait(queue_mutex);
	/* QUEUE PROTECTION INTRO END --- DO NOT TOUCH */

	/* WRITE YOUR CODE HERE! */
	/* MAKE SURE NOT TO RETURN WITHOUT GOING THROUGH THE OUTRO CODE! */
	sync_printf("Q:[");

	for (i = the_queue->rd_pos, j = 0; j < the_queue->max_size - the_queue->available;
	     i = (i + 1) % the_queue->max_size, ++j)
	{
		sync_printf("R%ld%s", the_queue->requests[i].request.req_id,
		       ((j+1 != the_queue->max_size - the_queue->available)?",":""));
	}

	sync_printf("]\n");

	/* QUEUE PROTECTION OUTRO START --- DO NOT TOUCH */
	sem_post(queue_mutex);
	/* QUEUE PROTECTION OUTRO END --- DO NOT TOUCH */
}

// function to get an image_id
uint64_t get_new_image_id() {
    static uint64_t img_id_counter = 1024;  // Start from 1024
    return img_id_counter++;
}

/* Main logic of the worker thread */
void * worker_main (void * arg)
{
	struct timespec now;
	struct worker_params * params = (struct worker_params *)arg;

	/* Print the first alive message. */
	clock_gettime(CLOCK_MONOTONIC, &now);
	sync_printf("[#WORKER#] %lf Worker Thread Alive!\n", TSPEC_TO_DOUBLE(now));

	/* Okay, now execute the main logic. */
	while (!params->worker_done) {

		struct request_meta req;
		struct response resp;
		req = get_from_queue(params->the_queue);

		/* Detect wakeup after termination asserted */
		if (params->worker_done) 
			break;

		clock_gettime(CLOCK_MONOTONIC, &req.start_timestamp);

		/* IMPLEMENT ME! Take the necessary steps to process
		 * the client's request for image processing. */

		// Processing the Request
		uint8_t err = 0;
		struct image * newImage = NULL;
		uint64_t new_img_id = req.request.img_id; // Default to the original image id

        /* Check if the image exists */
        if (req.request.img_op != IMG_RETRIEVE) {
            if (image_array[req.request.img_id] == NULL) {
                err = 1; // Image not found
            }
        }

		if (err == 0) {
			// Perform operation based on img_op
			switch(req.request.img_op) {
				case IMG_ROT90CLKW:
					// Handling Rotation
					newImage = rotate90Clockwise(image_array[req.request.img_id], &err);
					break;
				case IMG_BLUR:
					// Handling Image Blue
					newImage = blurImage(image_array[req.request.img_id], &err);
					break;
				case IMG_SHARPEN:
					// Handling Image Sharpen
					newImage = sharpenImage(image_array[req.request.img_id], &err);
					break;
				case IMG_VERTEDGES:
					// Detecting Verticle Edges
					newImage = detectVerticalEdges(image_array[req.request.img_id], &err);
					break;
				case IMG_HORIZEDGES:
					// Detecting Horizontal Edges
					newImage = detectHorizontalEdges(image_array[req.request.img_id], &err);
					break;
				case IMG_RETRIEVE:
					/* Handle image retrieval separately */
					if (image_array[req.request.img_id]) {
						/* Send response */
						
						// // Save the manipulated image
						// char filename[256];
						// snprintf(filename, sizeof(filename), "retrieved_image_%lu.bmp", req.request.img_id);
						// uint8_t save_result = saveBMP(filename, image_array[req.request.img_id]);

						// if (save_result != 0) {
						// 	// Handle error in saving the image
						// 	fprintf(stderr, "Error saving image to %s\n", filename);
						// }

						resp.req_id = req.request.req_id;
						resp.img_id = req.request.img_id;
						resp.ack = RESP_COMPLETED;
						send(params->conn_socket, &resp, sizeof(struct response), 0);

						/* Send the image */
						sendImage(image_array[req.request.img_id], params->conn_socket);

						/* Record completion timestamp */
						clock_gettime(CLOCK_MONOTONIC, &req.completion_timestamp);

						/* Print status report */
						sync_printf("T%d R%" PRIu64 ":%lf,%s,%d,%" PRIu64 ",%" PRIu64 ",%lf,%lf,%lf\n",
							params->worker_id,
							req.request.req_id,
							TSPEC_TO_DOUBLE(req.request.req_timestamp),
							OPCODE_TO_STRING(req.request.img_op),
							req.request.overwrite,
							req.request.img_id,
							req.request.img_id,
							TSPEC_TO_DOUBLE(req.receipt_timestamp),
							TSPEC_TO_DOUBLE(req.start_timestamp),
							TSPEC_TO_DOUBLE(req.completion_timestamp));

						dump_queue_status(params->the_queue);
					} else {
						// Image not found
						err = 1;
					}
					continue; // Move to the next request
				default:
					/* Unknown operation */
					err = 1;
					break;
			}

			if (err == 0 && newImage != NULL) {
				/* Handle overwrite logic */
				if (req.request.overwrite == 0) {
					/* Create a new image ID */
					new_img_id = get_new_image_id();
					image_array[new_img_id] = newImage;
				} else {
					/* Overwrite the original image */
					deleteImage(image_array[req.request.img_id]);
					image_array[req.request.img_id] = newImage;
					new_img_id = req.request.img_id;
				}
				
				/* Record completion timestamp */
				clock_gettime(CLOCK_MONOTONIC, &req.completion_timestamp);

				/* Send response */
				resp.req_id = req.request.req_id;
				resp.img_id = new_img_id;
				resp.ack = RESP_COMPLETED;
				send(params->conn_socket, &resp, sizeof(struct response), 0);

				/* Print status report */
				sync_printf("T%d R%" PRIu64 ":%lf,%s,%d,%" PRIu64 ",%" PRIu64 ",%lf,%lf,%lf\n",
					params->worker_id,
					req.request.req_id,
					TSPEC_TO_DOUBLE(req.request.req_timestamp),
					OPCODE_TO_STRING(req.request.img_op),
					req.request.overwrite,
					req.request.img_id,
					new_img_id,
					TSPEC_TO_DOUBLE(req.receipt_timestamp),
					TSPEC_TO_DOUBLE(req.start_timestamp),
					TSPEC_TO_DOUBLE(req.completion_timestamp));

				dump_queue_status(params->the_queue);
			} else {
				// Handle Error
				resp.req_id = req.request.req_id;
				resp.img_id = 0;
				resp.ack = RESP_REJECTED;
				send(params->conn_socket, &resp, sizeof(struct response), 0);
			}
		} else {
		    /* Handle error */
            resp.req_id = req.request.req_id;
            resp.img_id = 0;
            resp.ack = RESP_REJECTED;
            send(params->conn_socket, &resp, sizeof(struct response), 0);
        }
	}
	return NULL;
}


/* This function will start/stop all the worker threads wrapping
 * around the pthread_join/create() function calls */

int control_workers(enum worker_command cmd, size_t worker_count,
		    struct worker_params * common_params)
{
	/* Anything we allocate should we kept as static for easy
	 * deallocation when the STOP command is issued */
	static pthread_t * worker_pthreads = NULL;
	static struct worker_params ** worker_params = NULL;
	static int * worker_ids = NULL;


	/* Start all the workers */
	if (cmd == WORKERS_START) {
		size_t i;
		/* Allocate all structs and parameters */
		worker_pthreads = (pthread_t *)malloc(worker_count * sizeof(pthread_t));
		worker_params = (struct worker_params **)
		malloc(worker_count * sizeof(struct worker_params *));
		worker_ids = (int *)malloc(worker_count * sizeof(int));


		if (!worker_pthreads || !worker_params || !worker_ids) {
			ERROR_INFO();
			perror("Unable to allocate arrays for threads.");
			return EXIT_FAILURE;
		}


		/* Allocate and initialize as needed */
		for (i = 0; i < worker_count; ++i) {
			worker_ids[i] = -1;


			worker_params[i] = (struct worker_params *)
				malloc(sizeof(struct worker_params));


			if (!worker_params[i]) {
				ERROR_INFO();
				perror("Unable to allocate memory for thread.");
				return EXIT_FAILURE;
			}


			worker_params[i]->conn_socket = common_params->conn_socket;
			worker_params[i]->the_queue = common_params->the_queue;
			worker_params[i]->worker_done = 0;
			worker_params[i]->worker_id = i;
		}


		/* All the allocations and initialization seem okay,
		 * let's start the threads */
		for (i = 0; i < worker_count; ++i) {
			worker_ids[i] = pthread_create(&worker_pthreads[i], NULL, worker_main, worker_params[i]);


			if (worker_ids[i] < 0) {
				ERROR_INFO();
				perror("Unable to start thread.");
				return EXIT_FAILURE;
			} else {
				printf("INFO: Worker thread %ld (TID = %d) started!\n",
				       i, worker_ids[i]);
			}
		}
	}


	else if (cmd == WORKERS_STOP) {
		size_t i;


		/* Command to stop the threads issues without a start
		 * command? */
		if (!worker_pthreads || !worker_params || !worker_ids) {
			return EXIT_FAILURE;
		}


		/* First, assert all the termination flags */
		for (i = 0; i < worker_count; ++i) {
			if (worker_ids[i] < 0) {
				continue;
			}


			/* Request thread termination */
			worker_params[i]->worker_done = 1;
		}


		/* Next, unblock threads and wait for completion */
		for (i = 0; i < worker_count; ++i) {
			if (worker_ids[i] < 0) {
				continue;
			}


			sem_post(queue_notify);
		}


        for (i = 0; i < worker_count; ++i) {
            pthread_join(worker_pthreads[i],NULL);
            printf("INFO: Worker thread exited.\n");
        }


		/* Finally, do a round of deallocations */
		for (i = 0; i < worker_count; ++i) {
			free(worker_params[i]);
		}


		free(worker_pthreads);
		worker_pthreads = NULL;


		free(worker_params);
		worker_params = NULL;


		free(worker_ids);
		worker_ids = NULL;
	}


	else {
		ERROR_INFO();
		perror("Invalid thread control command.");
		return EXIT_FAILURE;
	}


	return EXIT_SUCCESS;
}
/* Main function to handle connection with the client. This function
 * takes in input conn_socket and returns only when the connection
 * with the client is interrupted. */
void handle_connection(int conn_socket, struct connection_params conn_params)
{
	struct request_meta * req;
	struct queue * the_queue;
	size_t in_bytes;
	int counter = 0; // initalize counter for img_id
	memset(image_array, 0, sizeof(image_array)); // initialize images array to null

	/* The connection with the client is alive here. Let's start
	 * the worker thread. */
	struct worker_params common_worker_params;
	int res;

	/* Now handle queue allocation and initialization */
	the_queue = (struct queue *)malloc(sizeof(struct queue));
	queue_init(the_queue, conn_params.queue_size, conn_params.queue_policy);

	common_worker_params.conn_socket = conn_socket;
	common_worker_params.the_queue = the_queue;
	res = control_workers(WORKERS_START, conn_params.workers, &common_worker_params);

	/* Do not continue if there has been a problem while starting
	 * the workers. */
	if (res != EXIT_SUCCESS) {
		free(the_queue);

		/* Stop any worker that was successfully started */
		control_workers(WORKERS_STOP, conn_params.workers, NULL);
		return;
	}

	/* We are ready to proceed with the rest of the request
	 * handling logic. */

	req = (struct request_meta *)malloc(sizeof(struct request_meta));

	do {
		in_bytes = recv(conn_socket, &req->request, sizeof(struct request), 0);
		clock_gettime(CLOCK_MONOTONIC, &req->receipt_timestamp);

		/* Don't just return if in_bytes is 0 or -1. Instead
		 * skip the response and break out of the loop in an
		 * orderly fashion so that we can de-allocate the req
		 * and resp varaibles, and shutdown the socket. */
		if (in_bytes > 0) {

			/* IMPLEMENT ME! Check right away if the
			 * request has img_op set to IMG_REGISTER. If
			 * so, handle the operation right away,
			 * reading in the full image payload, replying
			 * to the server, and bypassing the queue.
			 (
				Don't forget to send a response back to the client after
			  registering an image :) 
			 )
			  */
			clock_gettime(CLOCK_MONOTONIC, &req->start_timestamp);
			if (req->request.img_op == IMG_REGISTER) {
					// Handle IMG_REGISTER
					if (counter >= 1024) {
						// Send rejection response
						struct response resp = {req->request.req_id, 0, RESP_REJECTED};
						send(conn_socket, &resp, sizeof(struct response), 0);
						continue;
					}

					// Receive image
					struct image *image = recvImage(conn_socket);

					if (image != NULL) {
						// Successfully received image
						image_array[counter] = image;

						// Prepare and send response
						struct response resp = {req->request.req_id, counter, RESP_COMPLETED};
						clock_gettime(CLOCK_MONOTONIC, &req->completion_timestamp);
						send(conn_socket, &resp, sizeof(struct response), 0);

						// Print status report
						sync_printf("T1 R%" PRIu64 ":%lf,%s,%d,0,%" PRIu64 ",%lf,%lf,%lf\n",
							req->request.req_id,
							TSPEC_TO_DOUBLE(req->request.req_timestamp),
							OPCODE_TO_STRING(req->request.img_op),
							req->request.overwrite,
							resp.img_id,
							TSPEC_TO_DOUBLE(req->receipt_timestamp),
							TSPEC_TO_DOUBLE(req->start_timestamp),
							TSPEC_TO_DOUBLE(req->completion_timestamp));

						counter++;  // Increment image counter
					} else {
						// Failed to receive image, send rejection response
						struct response resp = {req->request.req_id, 0, RESP_REJECTED};
						send(conn_socket, &resp, sizeof(struct response), 0);
					}
				} else {
					// Enqueue the request
					res = add_to_queue(*req, the_queue);

					if (res) {
						// Queue is full, send rejection
						struct response resp = {req->request.req_id, 0, RESP_REJECTED};
						send(conn_socket, &resp, sizeof(struct response), 0);

						sync_printf("X%" PRIu64 ":%lf,%lf,%lf\n", req->request.req_id,
							TSPEC_TO_DOUBLE(req->request.req_timestamp),
							TSPEC_TO_DOUBLE(req->request.req_length),
							TSPEC_TO_DOUBLE(req->receipt_timestamp));
					}
				}
			}
		} while (in_bytes > 0);


	/* Stop all the worker threads. */
	control_workers(WORKERS_STOP, conn_params.workers, NULL);

	free(req);
	shutdown(conn_socket, SHUT_RDWR);
	close(conn_socket);
	printf("INFO: Client disconnected.\n");
}


/* Template implementation of the main function for the FIFO
 * server. The server must accept in input a command line parameter
 * with the <port number> to bind the server to. */
int main (int argc, char ** argv) {
	int sockfd, retval, accepted, optval, opt;
	in_port_t socket_port;
	struct sockaddr_in addr, client;
	struct in_addr any_address;
	socklen_t client_len;
	struct connection_params conn_params;
	conn_params.queue_size = 0;
	conn_params.queue_policy = QUEUE_FIFO;
	conn_params.workers = 1;

	/* Parse all the command line arguments */
	while((opt = getopt(argc, argv, "q:w:p:")) != -1) {
		switch (opt) {
		case 'q':
			conn_params.queue_size = strtol(optarg, NULL, 10);
			printf("INFO: setting queue size = %ld\n", conn_params.queue_size);
			break;
		case 'w':
			conn_params.workers = strtol(optarg, NULL, 10);
			printf("INFO: setting worker count = %ld\n", conn_params.workers);
			if (conn_params.workers != 1) {
				ERROR_INFO();
				fprintf(stderr, "Only 1 worker is supported in this implementation!\n" USAGE_STRING, argv[0]);
				return EXIT_FAILURE;
			}
			break;
		case 'p':
			if (!strcmp(optarg, "FIFO")) {
				conn_params.queue_policy = QUEUE_FIFO;
			} else {
				ERROR_INFO();
				fprintf(stderr, "Invalid queue policy.\n" USAGE_STRING, argv[0]);
				return EXIT_FAILURE;
			}
			printf("INFO: setting queue policy = %s\n", optarg);
			break;
		default: /* '?' */
			fprintf(stderr, USAGE_STRING, argv[0]);
		}
	}

	if (!conn_params.queue_size) {
		ERROR_INFO();
		fprintf(stderr, USAGE_STRING, argv[0]);
		return EXIT_FAILURE;
	}

	if (optind < argc) {
		socket_port = strtol(argv[optind], NULL, 10);
		printf("INFO: setting server port as: %d\n", socket_port);
	} else {
		ERROR_INFO();
		fprintf(stderr, USAGE_STRING, argv[0]);
		return EXIT_FAILURE;
	}

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

	/* Initilize threaded printf mutex */
	printf_mutex = (sem_t *)malloc(sizeof(sem_t));
	retval = sem_init(printf_mutex, 0, 1);
	if (retval < 0) {
		ERROR_INFO();
		perror("Unable to initialize printf mutex");
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
	/* DONE - Initialize queue protection variables */

	/* Ready to handle the new connection with the client. */
	handle_connection(accepted, conn_params);

	// Clean up images
	for (int i = 0; i < 1024; i++) {
		if (image_array[i] != NULL) {
			deleteImage(image_array[i]);
			image_array[i] = NULL;
		}
	}
	free(queue_mutex);
	free(queue_notify);

	close(sockfd);
	return EXIT_SUCCESS;
}
