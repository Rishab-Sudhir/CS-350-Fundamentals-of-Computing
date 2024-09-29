import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

################################################### Code from 1b
# Read the server output file containing the request data
# Structure: R<request_id>:<sent_timestamp>,<request_length>,<receipt_timestamp>,<completion_timestamp>

df = pd.read_csv('server_output.txt', header=None, names=['request_id', 'sent_timestamp', 'request_length', 'receipt_timestamp', 'completion_timestamp'], sep='[:,]', engine = 'python')

# extract the sent timestamp 
sent_timestamps = df['sent_timestamp'].astype(float)

# Compute the inter-arrival times

inter_arrival_times = sent_timestamps.diff().dropna() # Drop the first NaN value
max_iat = inter_arrival_times.max()

# Set x axis ticks ever 0.005
tick_positions = np.arange(0, max_iat + 0.05, 0.05)


# Define bins for the inter-arrival times, just like for request lengths
bins = np.arange(0, max_iat+0.05, 0.05) # Adjust bin size as necessary

# Compute the histogram
counts, bin_edges = np.histogram(inter_arrival_times, bins=bins)

normalized_counts = counts / 999
bin_centers = (bin_edges[:-1] + bin_edges[1:])/2

################################################### New Code

# Define the number of samples for theoretical distributions
num_samples = 10000
bin_width = bin_edges[1] - bin_edges[0]  # Get the bin width (0.05)

# generate samples from normal dist

mean_normal = 1/6
std_normal = 1
normal_samples = np.random.normal(loc=mean_normal, scale=std_normal, size=num_samples)

# Generate samples from the exponenetial dist

mean_exponential = 1/6
exponential_samples = np.random.exponential(scale=mean_exponential, size=num_samples)

# Genrate samples from the uniform dist

low_uniform = 0 # to center around mean 1/10
high_uniform = 2/6 # to center around mean 2/10
uniform_samples = np.random.uniform(low=low_uniform, high=high_uniform, size=num_samples)

# Compute the histograms for th theoretical distributions

normal_counts, _ = np.histogram(normal_samples, bins=bins, density=True)
exponential_counts, _ = np.histogram(exponential_samples, bins=bins, density=True)
uniform_counts, _ = np.histogram(uniform_samples, bins=bins, density=True)

# Scale the PDFs by the bin width to match the scale of the normalized data
normal_counts *= bin_width
exponential_counts *= bin_width
uniform_counts *= bin_width

# plt.figure(figsize=(16, 8)): Creates a figure with a larger size (16 units wide and 8 units tall).
plt.figure(figsize=(16,8))
plt.bar(bin_centers, normalized_counts, width=0.045, align='center', edgecolor='black', label='Inter-arrival time Data')

# Plot the theoretical distributions as lines
plt.plot(bin_centers, normal_counts, label='Normal Distribution', color='red', linewidth=2)
plt.plot(bin_centers, exponential_counts, label='Exponential Distribution', color='blue', linewidth=2)
plt.plot(bin_centers, uniform_counts, label='Uniform Distribution', color='green', linewidth=2)

plt.xticks(tick_positions, rotation='vertical')

plt.xlabel('Inter-arrival Time (seconds)')
plt.ylabel('Normalized Frequency')
plt.title('Distribution of Inter-arrival Times compared with Theoretical Distributions')
# Show the legend clearly
plt.legend(loc='best')
plt.grid(True)
plt.show()