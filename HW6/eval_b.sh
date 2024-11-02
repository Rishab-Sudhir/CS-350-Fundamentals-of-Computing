#!/bin/bash

# Ensure clean environment for each run
rm -f server_output_run1.log client_output_run1.log server_output_run2.log client_output_run2.log

# Run 1 with images_small directory
echo "Running Run 1 (images_small)..."
./build/server_img -q 100 1234 > server_output_run1.log 2>&1 &
SERVER_PID=$!
sleep 1  # Give the server a moment to start
./client -a 30 -I images_small/ -n 1000 1234 > client_output_run1.log 2>&1
wait $SERVER_PID

# Run 2 with images_all directory
echo "Running Run 2 (images_all)..."
./build/server_img -q 100 6789 > server_output_run2.log 2>&1 &
SERVER_PID=$!
sleep 1  # Give the server a moment to start
./client -a 30 -I images_all/ -n 1000 6789 > client_output_run2.log 2>&1
wait $SERVER_PID

echo "Experiments completed. Outputs saved as server_output_run1.log, client_output_run1.log, server_output_run2.log, client_output_run2.log."
