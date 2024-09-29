import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

################################################ Code from 1a
# read data into a dataframe
# Header = None (no header title)
# names = ['length'] assigns the column name 'length' to the data
df = pd.read_csv('request_lengths.txt', header=None, names=['length'])

# define bins
max_length = df['length'].max()

# Create the bins in intervals of 0.05
# np.arange(start, stop, step)
# An array of bin edges starting from 0, increasing in steps of 0.005, up to the maximum request length.
bins = np.arange(0, max_length  + 0.005, 0.005)

# compute histogram
# Counts = the number of data points in each bin
# bin_edges = the edges of the bins
counts, bin_edges = np.histogram(df['length'], bins=bins)

# Normalize the counts
normalized_counts = counts/counts.sum()

# Set x axis ticks ever 0.005
tick_positions = np.arange(0, max_length + 0.005, 0.005)

# plotting
# Calculates the center of each bin by averaging the left and right edges.
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

################################################ New Code

# Define the number of samples for theoretical distributions
num_samples = 10000
bin_width = bin_edges[1] - bin_edges[0]  # Get the bin width (0.005)

# generate samples from normal dist
"""
Generate samples from the Normal distribution:
np.random.normal() generates random samples from a normal distribution.
loc=mean_normal sets the mean of the distribution (1/10).
scale=std_normal sets the standard deviation (1).
size=num_samples specifies the number of samples to generate (10,000).
This creates a set of 10,000 random samples from a normal distribution with a mean of 1/10 and standard deviation of 1.
"""
mean_normal = 1/10
std_normal = 1
normal_samples = np.random.normal(loc=mean_normal, scale=std_normal, size=num_samples)

# Generate samples from the exponenetial dist
"""
Generate samples from the Exponential distribution:
np.random.exponential() generates random samples from an exponential distribution.
scale=mean_exponential sets the scale parameter, which is the inverse of the rate parameter λ. 
Since the mean of an exponential distribution is 1/λ, setting the scale to 
1/10 ensures a mean of 1/10.
This creates 10,000 samples from an exponential distribution with a mean of 1/10.
"""
mean_exponential = 1/10
exponential_samples = np.random.exponential(scale=mean_exponential, size=num_samples)

# Genrate samples from the uniform dist
"""
Generate samples from the Uniform distribution:
np.random.uniform() generates random samples from a uniform distribution.
low=low_uniform sets the lower bound of the distribution (0).
high=high_uniform sets the upper bound of the distribution (2/10), ensuring that the mean is centered around 1/10.
This creates 10,000 samples uniformly distributed between 0 and 2/10.
"""
low_uniform = 0 # to center around mean 1/10
high_uniform = 2/10 # to center around mean 2/10
uniform_samples = np.random.uniform(low=low_uniform, high=high_uniform, size=num_samples)

# Compute the histograms for th theoretical distributions
"""
Compute histograms for the theoretical distributions:
np.histogram() is used to calculate the histogram of each distribution (Normal, Exponential, and Uniform).
bins=bins ensures that all histograms use the same bins as the experimental data, so they can be compared directly.
density=True normalizes the histogram so that the area under the curve sums to 1, making it a probability density function (PDF) rather than a frequency count.
"""
normal_counts, _ = np.histogram(normal_samples, bins=bins, density=True)
exponential_counts, _ = np.histogram(exponential_samples, bins=bins, density=True)
uniform_counts, _ = np.histogram(uniform_samples, bins=bins, density=True)

# Scale the PDFs by the bin width to match the scale of the normalized data
normal_counts *= bin_width
exponential_counts *= bin_width
uniform_counts *= bin_width

# Plot the request length data as bars
plt.figure(figsize=(12, 6))  # Increase figure size for better readability

"""
Plot the experimental data:
plt.bar() is used to plot the experimental data as bars.
bin_centers: The positions of the bars on the x-axis (centered on each bin).
normalized_counts: The height of each bar, representing the normalized frequency.
width=0.004: The width of each bar is slightly smaller than the bin size to prevent overlap.
alpha=0.6: Sets the transparency of the bars, so that the lines can be more visible.
"""
plt.bar(bin_centers, normalized_counts, width=0.004, align='center', edgecolor='black', label='Request Length Data')

# Plot the theoretical distributions as lines
plt.plot(bin_centers, normal_counts, label='Normal Distribution', color='red', linewidth=2)
plt.plot(bin_centers, exponential_counts, label='Exponential Distribution', color='blue', linewidth=2)
plt.plot(bin_centers, uniform_counts, label='Uniform Distribution', color='green', linewidth=2)

# Only show ever other tick (each segment will then show 2 bars)
plt.xticks(tick_positions[::2], rotation='vertical')
plt.xlabel('Request Length (seconds)')
plt.ylabel('Normalized Frequency')
plt.title('Comparison of Request Data with Theoretical Distributions')
# Show the legend clearly
plt.legend(loc='best')
plt.grid(True)
plt.show()

