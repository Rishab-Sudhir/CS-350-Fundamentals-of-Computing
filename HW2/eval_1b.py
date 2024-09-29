import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the server output file containing the request data
# Structure: R<request_id>:<sent_timestamp>,<request_length>,<receipt_timestamp>,<completion_timestamp>
"""
sep='[:,]': Defines the separators for the fields, which are either : or , in the server output.
engine='python': Specifies the Python engine for parsing, which is more flexible when dealing with complex separators.
"""
df = pd.read_csv('server_output.txt', header=None, names=['request_id', 'sent_timestamp', 'request_length', 'receipt_timestamp', 'completion_timestamp'], sep='[:,]', engine = 'python')

# extract the sent timestamp 
sent_timestamps = df['sent_timestamp'].astype(float)

# Compute the inter-arrival times
"""
Calculating Inter-arrival Times:
sent_timestamps.diff(): This calculates the difference between consecutive timestamps, effectively giving us the inter-arrival times.
For example, if the first timestamp is 10 and the second is 15, the inter-arrival time is 15 - 10 = 5.
dropna(): Removes the first result, which is NaN because there's no previous timestamp to subtract from the first entry.
After applying diff(), the first row will have a NaN value because theres no prior timestamp to calculate the difference.
Now, inter_arrival_times contains the differences between each pair of consecutive sent timestamps, giving us the 999 inter-arrival times for 1000 requests.
"""
inter_arrival_times = sent_timestamps.diff().dropna() # Drop the first NaN value

max_iat = inter_arrival_times.max()

# Set x axis ticks ever 0.005
tick_positions = np.arange(0, max_iat + 0.05, 0.05)


# Define bins for the inter-arrival times, just like for request lengths
bins = np.arange(0, max_iat+0.05, 0.05) # Adjust bin size as necessary

# Compute the histogram
"""
Calculating the Histogram:
np.histogram(inter_arrival_times, bins=bins): Computes the histogram of the inter-arrival times.
inter_arrival_times: The data to be binned.
bins=bins: The bin edges we defined earlier.
counts: An array representing how many inter-arrival times fall into each bin.
bin_edges: The edges of the bins used to group the inter-arrival times.
"""
counts, bin_edges = np.histogram(inter_arrival_times, bins=bins)

normalized_counts = counts / 999
"""
Calculating the Bin Centers:
bin_edges[:-1]: All the bin edges except the last one.
bin_edges[1:]: All the bin edges except the first one.
(bin_edges[:-1] + bin_edges[1:]) / 2: Averages the left and right bin edges to get the center of each bin.
This is useful for plotting the bar chart where the bars are centered on the bins.
"""
bin_centers = (bin_edges[:-1] + bin_edges[1:])/2

# plt.figure(figsize=(16, 8)): Creates a figure with a larger size (16 units wide and 8 units tall).
plt.figure(figsize=(16,8))

"""
plt.bar(bin_centers, normalized_counts, width=0.004, align='center', edgecolor='black'):
Plots a bar chart with the bin centers on the x-axis and the normalized counts on the y-axis.
width=0.004: Sets the width of the bars (slightly less than the bin width to avoid overlap).
align='center': Ensures the bars are centered on the bin centers.
edgecolor='black': Adds a black outline to the bars for better visibility.
"""
plt.bar(bin_centers, normalized_counts, width=0.045, align='center', edgecolor='black')

plt.xticks(tick_positions, rotation='vertical')

plt.xlabel('Inter-arrival Time (seconds)')
plt.ylabel('Normalized Frequency')
plt.title('Distribution of Inter-arrival Times')

plt.grid(True)
plt.show()