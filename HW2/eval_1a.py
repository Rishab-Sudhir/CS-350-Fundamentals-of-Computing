import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

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

'''
plt.bar():
Plots a bar chart.
bin_centers: Positions of the bars on the x-axis.
normalized_counts: Heights of the bars.
width=0.004: Width of each bar (slightly less than the bin width of 0.005 to avoid overlap).
align='center': Centers the bars on the bin_centers.
edgecolor='black': Sets the edge color of the bars.
plt.grid(True):
Adds a grid to the plot for better readability.
plt.show():
Displays the plot.
'''
plt.bar(bin_centers, normalized_counts, width=0.004, align='center', edgecolor='black')

# Only show ever other tick (each segment will then show 2 bars)
plt.xticks(tick_positions[::2], rotation='vertical')
plt.xlabel('Request Length (seconds)')
plt.ylabel('Normalized Frequency')
plt.title('Distribution of Request Lengths')

plt.grid(True)
plt.show()

print(f"Maximum request length: {df['length'].max()}")
print("Bins:", bins)
print("Counts:", counts)
