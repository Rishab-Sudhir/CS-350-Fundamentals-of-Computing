#!/bin/bash

# Output CSV file
OUTPUT_FILE="clock_data_busy.csv" # change depending on output

# Remove the output file if it exists
if [ -f "$OUTPUT_FILE" ]; then
    rm "$OUTPUT_FILE"
fi

# Write the CSV header
echo "WaitTime,ClocksElapsed,ClockSpeedMHz" >> "$OUTPUT_FILE"

# Loop over wait times from 1 to 10 seconds
for wait_time in {1..10}; do
    # Run the clock executable with the SLEEP/BUSY method ('s/b')
    OUTPUT=$(./build/clock "$wait_time" 0 b)
    
    # Check if the command ran successfully
    if [ $? -ne 0 ]; then
        echo "Error running ./build/clock with wait time $wait_time"
        continue
    fi
    
    # Parse the output to extract ClocksElapsed and ClockSpeed
    clocks_elapsed=$(echo "$OUTPUT" | grep 'ClocksElapsed:' | awk -F':' '{print $2}' | tr -d ' ')
    clock_speed=$(echo "$OUTPUT" | grep 'ClockSpeed:' | awk -F':' '{print $2}' | tr -d ' ')
    
    # Append the data to the CSV file
    echo "$wait_time,$clocks_elapsed,$clock_speed" >> "$OUTPUT_FILE"
    
    echo "Collected data for wait time $wait_time seconds"
done

echo "Data collection complete. Data saved to $OUTPUT_FILE"
