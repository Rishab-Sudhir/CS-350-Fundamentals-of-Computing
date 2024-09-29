def parse_server_log_for_utilization(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    first_receipt_timestamp = None
    last_completion_timestamp = None
    total_busy_time = 0.0  # Accumulate busy time here

    for line in lines:
        # Split the line to extract timestamp information
        parts = line.split(':')
        if len(parts) < 2:
            continue

        # Further split to extract individual fields
        timestamp_info = parts[1].split(',')

        # Extract the relevant fields
        receipt_timestamp = float(timestamp_info[2])
        completion_timestamp = float(timestamp_info[3])
        request_length = float(timestamp_info[1])  # Request length in seconds

        # Track the first and last timestamps
        if first_receipt_timestamp is None:
            first_receipt_timestamp = receipt_timestamp
        last_completion_timestamp = completion_timestamp

        # Sum the total busy time
        total_busy_time += request_length

    # Calculate total active time window
    total_time = last_completion_timestamp - first_receipt_timestamp

    # Calculate server utilization as a percentage
    utilization = (total_busy_time / total_time) * 100

    return utilization, total_time, total_busy_time

# usage
file_path = 'server_output.log'
utilization, total_time, total_busy_time = parse_server_log_for_utilization(file_path)

print(f"Total Time Window: {total_time} seconds")
print(f"Total Busy Time: {total_busy_time} seconds")
print(f"Server Utilization: {utilization}%")
