import os
import re
import pandas as pd 
import matplotlib.pyplot as plt 

# Define the directory containing the server output files
output_dir = '1c_output_files'

# Intialize list to store results
arrival_rates = list(range(10, 20))
average_response_times_d0 = []
average_response_times_d1 = []

# Define regex pattern to extract relevant data from the server output
pattern = r'R(\d+):([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+)'


# Loop through arrival rates from 10 to 19
for arrival_rate in range(10,20):
    for dist in [0,1]:
        # Define the filename
        filename = f"1c_server_output_d{dist}_a{arrival_rate}.txt"
        filepath = os.path.join(output_dir, filename)

        # Initialize a list to store response times
        response_times = []

        # Read the file and extract response times
        with open(filepath, 'r') as file:
            for line in file:
                match = re.match(pattern, line)
                if match:
                    receipt_timestamp = float(match.group(4))
                    completion_timestamp = float(match.group(6))
                    response_time = completion_timestamp - receipt_timestamp
                    response_times.append(response_time)
        
        # Calculate the average response time for the current arrival rate and dist
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Store the result
        if dist == 0:
            average_response_times_d0.append(avg_response_time)
        else:
            average_response_times_d1.append(avg_response_time)

# Calculate server utilization (U = lambda / mu, where mu = 20)
service_rate = 20
utilization = [arr_rate / service_rate for arr_rate in arrival_rates]


# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(utilization, average_response_times_d0, marker='o', linestyle='-', color='b', label='Exponential Distribution (-d 0)')
plt.plot(utilization, average_response_times_d1, marker='o', linestyle='-', color='r', label='Distribution 1 (-d 1)')

plt.xlabel('Server Utilization (λ / μ)')
plt.ylabel('Average Response Time (seconds)')
plt.title('Average Response Time vs. Server Utilization')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()