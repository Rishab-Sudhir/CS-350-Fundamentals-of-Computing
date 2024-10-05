import re
import matplotlib.pyplot as plt

server_output_file = '1e_server_output.txt' 

# Initialize counters and lists
total_requests = 0
rejected_requests = 0
rejection_timestamps = []

# Pattern for accepted requests
accepted_pattern = r'^R(\d+):([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+)'
# Pattern for rejected requests
rejected_pattern = r'^X(\d+):([\d\.]+),([\d\.]+),([\d\.]+)'

# Read the server output file
with open(server_output_file, 'r') as file:
    for line in file:
        # Check for accepted requests
        accepted_match = re.match(accepted_pattern, line)
        if accepted_match:
            total_requests += 1
            continue  # Move to next line

        # Check for rejected requests
        rejected_match = re.match(rejected_pattern, line)
        if rejected_match:
            total_requests += 1
            rejected_requests += 1

            # Extract the reject timestamp
            reject_timestamp = float(rejected_match.group(4))
            rejection_timestamps.append(reject_timestamp)

# Calculate the rejection ratio
rejection_ratio = rejected_requests / total_requests if total_requests > 0 else 0

print(f"Total Requests: {total_requests}")
print(f"Rejected Requests: {rejected_requests}")
print(f"Rejection Ratio: {rejection_ratio:.4f}")

# Calculate inter-rejection times
# Sort the rejection timestamps in case they're out of order
rejection_timestamps.sort()

"""
zip(rejection_timestamps[:-1], rejection_timestamps[1:]):
The zip() function combines two or more iterables (like lists) into an iterator of tuples.
In this case, it pairs each element from rejection_timestamps[:-1] with the corresponding element from rejection_timestamps[1:].
Effectively, it creates pairs of consecutive rejection timestamps.

# Given:
rejection_timestamps[:-1] = [t0, t1, t2, t3]
rejection_timestamps[1:]  = [t1, t2, t3, t4]

# zip() pairs:
zip(rejection_timestamps[:-1], rejection_timestamps[1:])  # Results in [(t0, t1), (t1, t2), (t2, t3), (t3, t4)]

"""
inter_rejection_times = [t2 - t1 for t1, t2 in zip(rejection_timestamps[:-1], rejection_timestamps[1:])]

# Plot the distribution of inter-rejection times
plt.figure(figsize=(10, 6))
plt.hist(inter_rejection_times, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.title('Distribution of Inter-Rejection Times')
plt.xlabel('Inter-Rejection Time (seconds)')
plt.ylabel('Frequency')
plt.grid(True)
plt.tight_layout()
plt.show()
