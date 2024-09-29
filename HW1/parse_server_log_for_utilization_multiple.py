import matplotlib.pyplot as plt

def parse_server_log_for_utlization(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    first_receipt_timestamp = None
    last_completion_timestamp = None
    total_busy_time = 0.0 # accumulates busy time

    for line in lines: 
        # split the line to extract time stamp info

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
            receipt_timestamp = float(timestamp_info[2])
            completion_timestamp = float(timestamp_info[3])
            request_length = float(timestamp_info[1]) # Request length in seconds

            # Track the first and last timestamps
            if first_receipt_timestamp is None:
                first_receipt_timestamp = receipt_timestamp
            last_completion_timestamp = completion_timestamp

            total_busy_time += request_length

        except  ValueError:
            continue
        
        # Checking if we valid timestamps to process
        if first_receipt_timestamp is None or last_completion_timestamp is None:
            return None, None, None
        
        # Calculate total active time window
        total_time = last_completion_timestamp - first_receipt_timestamp

        # Calculate server utilization as a percentage
        utilization = (total_busy_time/total_time) * 100

    return utilization, total_time, total_busy_time
    
arrival_rates = range(1, 13) # 1 to 12
utilizations = []

for arrival_rate in arrival_rates:

    file_path = f'./eval_server_output/server_output_{arrival_rate}.log' # for each of the server outputs

    utilization, total_time, total_busy_time = parse_server_log_for_utlization(file_path)

    if utilization is not None:
        utilizations.append(utilization)
        print(f"Arrival Rate: {arrival_rate}, Utilization: {utilization:.2f}%")
    else:
        utilizations.append(0)
        print(f"Arrival Rate: {arrival_rate}, Utilization: Could not be calculated.")

# plot the results
plt.figure(figsize=(10,6))
plt.plot(arrival_rates, utilizations, marker='o', linestyle='-', color='b')
plt.title('Server Utilization vs, Arrival Rate')
plt.xlabel('Arrival Rate (-a parameter)')
plt.ylabel('Server Utilization (%)')
plt.grid(True)
plt.show()