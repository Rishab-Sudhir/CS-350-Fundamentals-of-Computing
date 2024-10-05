from scipy.stats import expon, norm, uniform
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 

# Load the server log
file_path = './1a_Server_Output.txt'

# Lists to store extracted data
request_ids = []
sent_timestamps = []
request_lengths = []

# regex pattern to extract the data
pattern = r'R(\d+):([\d\.]+),([\d\.]+),'

# Extract data from the log file
with open(file_path, 'r') as file:
    for line in file:
        match = re.match(pattern, line)
        if match:
            request_ids.append(int(match.group(1)))
            sent_timestamps.append(float(match.group(2)))
            request_lengths.append(float(match.group(3)))

# create a dataFrame for analysis

data = pd.DataFrame({
    'Request_ID' : request_ids,
    'Sent_Timestamp': sent_timestamps,
    'Request_Length': request_lengths
})

# Calculate inter-arrival times
data['Inter_Arrival_Time'] = data['Sent_Timestamp'].diff()

# Plot histograms for Inter-Arrival Times and Request Length
plt.figure(figsize=(12,5))

# Inter-Arrival Times Histogram
plt.subplot(1,2,1)
sns.histplot(data['Inter_Arrival_Time'].dropna(), kde=True, bins=30)
plt.title('Inter-Arrival Times Distribution')
plt.xlabel('Inter-Arrival Time (seconds)')
plt.ylabel('Frequency')

# Request Length Histogram
plt.subplot(1,2,2)
sns.histplot(data['Request_Length'], kde=True, bins=30)
plt.title('Request Lengths Distribution')
plt.xlabel('Request Length')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()

############# Fitting Inter-Arrival Times to Exponential and Normal Distributions

# Extract the inter-arrival times, removing any NaN values.
inter_arrival_times = data['Inter_Arrival_Time'].dropna()

# Exponential Fit
"""
expon.fit(inter_arrival_times): Fits the exponential distribution to the data using scipy.stats.expon.fit(). It estimates the parameters of the distribution that best fit the given data. For an exponential distribution, the parameters returned are:
Location parameter (loc): Usually represents the starting point of the distribution.
Scale parameter (scale): Corresponds to 1/λ (where λ is the rate parameter).
"""
exp_params = expon.fit(inter_arrival_times)

# Extract the Scale parameter - the mean
exp_mean = exp_params[1]
print(f'exp_mean = {exp_mean}')
# Compute the PDF for exponential
"""
np.linspace(inter_arrival_times.min(), inter_arrival_times.max(), 100): 
Creates an array of 100 evenly spaced values between the minimum and maximum inter-arrival times, which we use as the x-values for plotting.
expon.pdf(..., *exp_params): 
Computes the probability density function (PDF) of the exponential distribution at the given x-values, using the previously obtained parameters (*exp_params).
"""
exp_pdf = expon.pdf(np.linspace(inter_arrival_times.min(), inter_arrival_times.max(), 100), *exp_params)

# Normal Fit
norm_params = norm.fit(inter_arrival_times)

# Mean and STD
norm_mean, norm_std = norm_params
norm_pdf = norm.pdf(np.linspace(inter_arrival_times.min(), inter_arrival_times.max(), 100), *norm_params)

plt.figure(figsize=(10, 5))
"""
sns.histplot(..., kde=False, bins=30, ...): Plots a histogram of the inter-arrival times data using 30 bins. The kde=False parameter means that a kernel density estimate is not plotted.
stat="density": Normalizes the histogram to show density rather than counts.
"""
sns.histplot(inter_arrival_times, kde=False, bins=30, color='skyblue', label='Inter-Arrival Times Data', stat="density")

"""
plt.plot(...): Plots the fitted exponential (red solid line) and normal (green dashed line) distributions.
'r-' and 'g--' specify the line colors (r for red, g for green) and styles (- for solid, -- for dashed).
lw=2: Sets the line width to 2.
"""
plt.plot(np.linspace(inter_arrival_times.min(), inter_arrival_times.max(), 100), exp_pdf, 'r-', lw=2, label='Exponential Fit')
plt.plot(np.linspace(inter_arrival_times.min(), inter_arrival_times.max(), 100), norm_pdf, 'g--', lw=2, label='Normal Fit')

plt.title('Fitting Inter-Arrival Times Distribution')
plt.xlabel('Request Length')
plt.ylabel('Density')
plt.legend()
plt.show()

############ Fitting Request Lengths to Uniform Distribution

# Extract the request lengths
request_lengths = data['Request_Length']

# Uniform Fit
"""
uniform.fit(request_lengths): Fits a uniform distribution to the request lengths, estimating:
Location parameter (loc): The minimum value of the distribution.
Scale parameter (scale): The range (i.e., difference between max and min).
"""
uniform_params = uniform.fit(request_lengths)

uniform_min, uniform_range = uniform_params
print(f'uniform_range: {uniform_range}')

uniform_pdf = uniform.pdf(np.linspace(request_lengths.min(), request_lengths.max(), 100), *uniform_params)

# Plotting the fit for request Lengths
plt.figure(figsize=(10, 5))
sns.histplot(request_lengths, kde=False, bins=30, color='lightgreen', label='Request Lengths Data', stat="density")

plt.plot(np.linspace(request_lengths.min(), request_lengths.max(), 100), uniform_pdf, 'b-', lw=2, label='Uniform Fit')

plt.title('Fitting Request Lengths Distribution')
plt.xlabel('Request Length')
plt.ylabel('Density')
plt.legend()
plt.show()
