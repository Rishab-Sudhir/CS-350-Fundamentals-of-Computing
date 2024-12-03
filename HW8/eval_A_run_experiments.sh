#!/bin/bash
# Had to change implementation as the parse_img_script() function in the client
# wasnt working, so manually creating scripts here.
# Ensure no server is running
pkill server_mimg

# Define the sections
Intro="0:R:1:6,0:R:1:7,0:R:1:8,0:R:1:9,0:R:1:10,0:R:1:11,0:R:1:12,0:R:1:13,0:R:1:14,0.5:R:1:15,"

Mid="0:r:1:0,0:b:1:0,0:s:1:0,0:v:1:0,0:h:1:0,0:r:1:0,0:b:1:0,0:s:1:0,0:v:1:0,0:h:1:0,\
0:r:1:1,0:b:1:1,0:s:1:1,0:v:1:1,0:h:1:1,0:r:1:1,0:b:1:1,0:s:1:1,0:v:1:1,0:h:1:1,\
0:r:1:2,0:b:1:2,0:s:1:2,0:v:1:2,0:h:1:2,0:r:1:2,0:b:1:2,0:s:1:2,0:v:1:2,0:h:1:2,\
0:r:1:3,0:b:1:3,0:s:1:3,0:v:1:3,0:h:1:3,0:r:1:3,0:b:1:3,0:s:1:3,0:v:1:3,0:h:1:3,\
0:r:1:4,0:b:1:4,0:s:1:4,0:v:1:4,0:h:1:4,0:r:1:4,0:b:1:4,0:s:1:4,0:v:1:4,0:h:1:4,\
0:r:1:5,0:b:1:5,0:s:1:5,0:v:1:5,0:h:1:5,0:r:1:5,0:b:1:5,0:s:1:5,0:v:1:5,0:h:1:5,\
0:r:1:6,0:b:1:6,0:s:1:6,0:v:1:6,0:h:1:6,0:r:1:6,0:b:1:6,0:s:1:6,0:v:1:6,0:h:1:6,\
0:r:1:7,0:b:1:7,0:s:1:7,0:v:1:7,0:h:1:7,0:r:1:7,0:b:1:7,0:s:1:7,0:v:1:7,0:h:1:7,\
0:r:1:8,0:b:1:8,0:s:1:8,0:v:1:8,0:h:1:8,0:r:1:8,0:b:1:8,0:s:1:8,0:v:1:8,0:h:1:8,\
0:r:1:9,0:b:1:9,0:s:1:9,0:v:1:9,0:h:1:9,0:r:1:9,0:b:1:9,0:s:1:9,0:v:1:9,0:h:1:9,"

Outro="0:T:1:0,0:T:1:1,0:T:1:2,0:T:1:3,0:T:1:4,0:T:1:5,0:T:1:6,0:T:1:7,0:T:1:8,0:T:1:9"

# Loop over runs 1 to 10
for N in {1..10}
do
    echo "Starting run $N"

    # Start the server with the time utility and redirect output
    /usr/bin/time -v ./build/server_mimg -q 1500 -w 1 -p FIFO 1234 > eval_A_server_output_run${N}.txt 2>&1 &
    SERVER_PID=$!

    # Give the server a moment to start
    sleep 1

    # Create the script by repeating Mid N times
    MidRepeated=""
    for ((i=1; i<=N; i++))
    do
        MidRepeated="${MidRepeated}${Mid}"
    done

    # Concatenate the sections
    SCRIPT="${Intro}${MidRepeated}${Outro}"

    # Run the client with the script (client runs in the foreground)
    ./client 1234 -I ./images/ -L "${SCRIPT}"

    # Wait for the client to finish (since it's in the foreground, this is implicit)

    # Wait for the server to finish processing (optional)
    sleep 1

    # Kill the server process
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null

    echo "Completed run $N"

    # Optionally, clean up or move output files
done
