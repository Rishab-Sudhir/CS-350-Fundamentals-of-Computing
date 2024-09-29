import numpy as np
import matplotlib.pyplot as plt

def parse_response_times(file_path):
    response_times = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.split(':')
        if len(parts) < 2:
            continue

        timestamp_info = parts[1].split(',')
        if len(timestamp_info) < 4:
            continue

        try:
            sent_timestamp = float(timestamp_info[0])
            completion_timestamp = float(timestamp_info[3])

            response_time = completion_timestamp - sent_timestamp
            response_times.append(response_time)

        except ValueError:
            continue

    return response_times


# Arrival rates from 1 to 12
arrival_rates = range(1, 13)
avg_response_times = []
server_utilizations = [7.99, 15.98, 23.96, 31.95, 39.93, 47.91, 55.88, 63.79, 71.58, 79.29, 86.93, 94.54]  # utilization values from Part d

# Process each run (for each `-a` value from 1 to 12)
for arrival_rate in arrival_rates:
    file_path = f'./eval_server_output/server_output_{arrival_rate}.log'  # Adjust the path as needed
    response_times = parse_response_times(file_path)

    if response_times:
        avg_response_time = np.mean(response_times)
        avg_response_times.append(avg_response_time)
        print(f"Arrival Rate: {arrival_rate}, Avg. Response Time: {avg_response_time:.6f} seconds")
    else:
        avg_response_times.append(0)
        print(f"Arrival Rate: {arrival_rate}, Avg. Response Time: Could not be calculated.")

# Plotting the average response time vs server utilization
plt.figure(figsize=(10, 6))
plt.plot(server_utilizations, avg_response_times, marker='o', linestyle='-', color='r')
plt.title('Average Response Time vs Server Utilization')
plt.xlabel('Server Utilization (%)')
plt.ylabel('Average Response Time (seconds)')
plt.grid(True)
plt.show()
