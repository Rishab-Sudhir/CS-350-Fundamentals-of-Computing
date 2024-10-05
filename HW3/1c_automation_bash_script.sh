#!/bin/bash

# Script to automate server-client experiment runs and save the results to output files

# Define the port number and queue size
PORT=2222
QUEUE_SIZE=1000

# Define the output directory
OUTPUT_DIR="1c_output_files"

# Create the output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Define arrival rate range
START_ARR_RATE=10
END_ARR_RATE=19

# Loop for both distribution types (-d 0 and -d 1)
for DIST in 0 1
do
    # Loop through arrival rates from 10 to 19
    for ARR_RATE in $(seq $START_ARR_RATE $END_ARR_RATE)
    do

        # Run the server and save the output to a file
        SERVER_OUTPUT_FILE="$OUTPUT_DIR/1c_server_output_d${DIST}_a${ARR_RATE}.txt"
        ./build/server_lim -q $QUEUE_SIZE $PORT > $SERVER_OUTPUT_FILE & SERVER_PID=$!
    
        # Give the server a moment to start
        sleep 1

        # Run the client
        ./client -a $ARR_RATE -s 20 -n 1500 -d $DIST $PORT
        
        # Kill the server process 
        kill $SERVER_PID

        # Give the server a moment to shut down
        sleep 1
    done
done

echo "All experiments completed. Results saved in $OUTPUT_DIR."