/*******************************************************************************
* Simple FIFO Order Server Implementation
*
* Description:
*     A server implementation designed to process client requests in First In,
*     First Out (FIFO) order. The server binds to the specified port number
*     provided as a parameter upon launch.
*
* Usage:
*     <build directory>/server <port_number>
*
* Parameters:
*     port_number - The port number to bind the server to.
*
* Author:
*     Renato Mancuso
*
* Affiliation:
*     Boston University
*
* Creation Date:
*     September 10, 2023
*
* Last Update:
*     September 9, 2024
*
* Notes:
*     Ensure to have proper permissions and available port before running the
*     server. The server relies on a FIFO mechanism to handle requests, thus
*     guaranteeing the order of processing. For debugging or more details, refer
*     to the accompanying documentation and logs.
*
*******************************************************************************/

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <inttypes.h>      // For format specifiers like PRIu64 used in printf()

/* Include struct definitions and other libraries that need to be
 * included by both client and server */
#include "common.h"

#define BACKLOG_COUNT 100
#define USAGE_STRING				    \
	"Missing parameter. Exiting.\n"		\
	"Usage: %s <port_number>\n"

/* Main function to handle connection with the client. This function
 * takes in input conn_socket and returns only when the connection
 * with the client is interrupted. */
static void handle_connection(int conn_socket)
{
	ssize_t bytes_received, bytes_sent;
	struct request req;
	struct response res;
	struct timespec receipt_timestamp, completion_timestamp;
	char sent_timestamp_str[32];
	char request_length_str[32];
	char receipt_timestamp_str[32];
	char completion_timestamp_str[32];

	while(1){
		// Receive the request from the client
		bytes_received = recv(conn_socket, &req, sizeof(req), 0);

		if (bytes_received == 0) {
			// Connection closed by client
			printf("INFO: Client disconnected.\n");
			break;
		} else if (bytes_received < 0) {
			perror("recv failed");
			break;
		} else if (bytes_received != sizeof(req)) {
			fprintf(stderr, "ERROR: Incomplete request received.\n");
			break;
		}

		// Record the receipt timestamp
		clock_gettime(CLOCK_MONOTONIC, &receipt_timestamp);

		// Perform busy-wait for the specified request length
		get_elapsed_busywait(req.request_length.tv_sec, req.request_length.tv_nsec);

		// Record the completion timestamp
		clock_gettime(CLOCK_MONOTONIC, &completion_timestamp);

		// Prepare the response
		res.request_id = req.request_id;
		res.reserved = 0;
		res.ack = 0; // Indicate success

		// Send the response back to the client
		bytes_sent = send(conn_socket, &res, sizeof(res), 0);
		if (bytes_sent < 0) {
			perror("send failed");
			break;
		}

		// Format timestamps for output
		snprintf(sent_timestamp_str, sizeof(sent_timestamp_str), "%.6f", TSPEC_TO_DOUBLE(req.sent_timestamp));
		snprintf(request_length_str, sizeof(request_length_str), "%.6f", TSPEC_TO_DOUBLE(req.request_length));
		snprintf(receipt_timestamp_str, sizeof(receipt_timestamp_str), "%.6f", TSPEC_TO_DOUBLE(receipt_timestamp));
		snprintf(completion_timestamp_str, sizeof(completion_timestamp_str), "%.6f", TSPEC_TO_DOUBLE(completion_timestamp));

		// Output the required information
		printf("R%" PRIu64 ":%s,%s,%s,%s\n",
			req.request_id,
			sent_timestamp_str,
			request_length_str,
			receipt_timestamp_str,
			completion_timestamp_str);
	}
	
	// Close the connection socket
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

	/* Get port to bind our socket to */
	if (argc > 1) {
		socket_port = strtol(argv[1], NULL, 10);
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

	/* Ready to handle the new connection with the client. */
	handle_connection(accepted);

	close(sockfd);
	return EXIT_SUCCESS;

}
