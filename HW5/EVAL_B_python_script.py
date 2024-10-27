import os
import re
import numpy as np
import matplotlib.pyplot as plt

# Parameters
POLICIES = ["FIFO", "SJN"]
ARRIVAL_RATES = [22, 24, 26, 28, 30, 32, 34, 36, 38, 40]

WORKERS = 2

# Initialize data structures
data = {policy: {'utilization': [], 'response_time': []} for policy in POLICIES}

# Regular expressions to parse log files
request_pattern = re.compile(r'R(\d+):([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+)')
worker_pattern = re.compile(r'T(\d+) R(\d+):([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+)')

for policy in POLICIES:
    for arr_rate in ARRIVAL_RATES:
        server_log_path = f'Eval_B_logs/{policy}/server_{arr_rate}.log'
        worker_busy_times = {}
        total_response_time = 0.0
        num_requests = 0
        start_times = []
        completion_times = []

        with open(server_log_path, 'r') as f:
            for line in f:
                # Match lines indicating request completion
                match = worker_pattern.match(line.strip())
                if match:
                    # Extract data
                    worker_id = int(match.group(1))
                    req_id = int(match.group(2))
                    req_timestamp = float(match.group(3))
                    req_length = float(match.group(4))
                    receipt_time = float(match.group(5))
                    start_time = float(match.group(6))
                    completion_time = float(match.group(7))

                    # Calculate busy time for this request
                    busy_time = completion_time - start_time

                    # Update worker busy times
                    if worker_id not in worker_busy_times:
                        worker_busy_times[worker_id] = 0.0
                    worker_busy_times[worker_id] += busy_time

                    # Calculate response time
                    response_time = completion_time - req_timestamp
                    total_response_time += response_time
                    num_requests += 1

                    start_times.append(start_time)
                    completion_times.append(completion_time)

        # Calculate total busy time
        total_busy_time = sum(worker_busy_times.values())

        # Calculate total runtime
        if completion_times:
            total_runtime = max(completion_times) - min(start_times)
            total_capacity = total_runtime * WORKERS
            server_utilization = total_busy_time / total_capacity
        else:
            server_utilization = 0.0

        # Calculate average response time
        if num_requests > 0:
            avg_response_time = total_response_time / num_requests
        else:
            avg_response_time = 0.0

        data[policy]['utilization'].append(server_utilization)
        data[policy]['response_time'].append(avg_response_time)
        print(f"Policy: {policy}, Arrival Rate: {arr_rate}, Utilization: {server_utilization:.4f}, Avg Response Time: {avg_response_time:.4f}")

# Plotting
plt.figure(figsize=(10, 6))

for policy in POLICIES:
    plt.plot(data[policy]['utilization'], data[policy]['response_time'], marker='o', label=policy)

plt.xlabel('Server Utilization')
plt.ylabel('Average Response Time')
plt.title('Average Response Time vs Server Utilization')
plt.legend()
plt.grid(True)
plt.savefig('response_time_vs_utilization.png')
plt.show()
