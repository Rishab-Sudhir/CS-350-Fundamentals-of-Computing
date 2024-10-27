#!/bin/bash

# Ensure the script is executable
# chmod +x run_experiments.sh

# Parameters
SERVER_EXEC="./build/server_pol"
CLIENT_EXEC="./client"
PORT=2222
QUEUE_SIZE=100
WORKERS=2
SERVICE_TIME=20
NUM_REQUESTS=1500
ARRIVAL_RATES=(22 24 26 28 30 32 34 36 38 40)
POLICIES=("FIFO" "SJN")

# Create a directory to store logs
mkdir -p Eval_B_logs

# Loop over policies
for POLICY in "${POLICIES[@]}"; do
    echo "Running experiments for policy: $POLICY"

    # Create a directory for the policy logs
    mkdir -p Eval_B_logs/$POLICY

    # Loop over arrival rates
    for ARR_RATE in "${ARRIVAL_RATES[@]}"; do
        echo "Running with arrival rate: $ARR_RATE"

        # Define log file names
        SERVER_LOG="Eval_B_logs/$POLICY/server_${ARR_RATE}.log"

        # Start the server in the background and redirect output to log file
        $SERVER_EXEC -w $WORKERS -q $QUEUE_SIZE -p $POLICY $PORT > $SERVER_LOG 2>&1 &
        SERVER_PID=$!

        # Wait for the server to be ready (you might need to adjust this sleep time)
        sleep 1

        # Run the client and redirect output to log file
        $CLIENT_EXEC -a $ARR_RATE -s $SERVICE_TIME -n $NUM_REQUESTS $PORT

        # Wait for the client to finish
        wait $CLIENT_PID

        # Stop the server
        kill $SERVER_PID
        wait $SERVER_PID 2>/dev/null

        # Optional: Wait a bit before starting the next experiment
        sleep 1
    done
done
