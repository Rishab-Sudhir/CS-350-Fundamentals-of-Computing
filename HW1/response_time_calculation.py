import numpy as np

def parse_response_times(file_path):
    # list to store response times
    response_times = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Split the line to extract timestamp information
        parts = line.split(':')
        if len(parts) < 2:
            continue

        # Further split to extract individual fields
        timestamp_info = parts[1].split(',')

        # Check if the line contains the expected number of fields
        if len(timestamp_info) < 4:
            continue

        try:
            # Extract the relevant fields
            sent_timestamp = float(timestamp_info[0])  # Sent_timestamp
            completion_timestamp = float(timestamp_info[3])  # Completion timestamp

            # Calculate response time
            response_time = completion_timestamp - sent_timestamp
            # Append response time
            response_times.append(response_time)

        except ValueError:
            continue

    return response_times


# Path to the log file where -a was set to 10
file_path = './eval_server_output/server_output_10.log'

# Get response times
response_times = parse_response_times(file_path)

# Compute statistics if response times are available
if response_times:
    avg_response_time = np.mean(response_times)
    max_response_time = np.max(response_times)
    min_response_time = np.min(response_times)
    std_dev_response_time = np.std(response_times)

    # Print the results
    print(f"Average Response Time: {avg_response_time:.6f} seconds")
    print(f"Max Response Time: {max_response_time:.6f} seconds")
    print(f"Min Response Time: {min_response_time:.6f} seconds")
    print(f"Standard Deviation of Response Times: {std_dev_response_time:.6f} seconds")
else:
    print("No response times found in the log file.")
