import re
import matplotlib.pyplot as plt

run_numbers = []
runtimes = []

for N in range(1, 11):
    filename = f'./Eval_C_server_outputs/Eval_C_server_output_run{N}.txt'
    with open(filename, 'r') as f:
        content = f.read()
        match = re.search(r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(\d+):(\d+\.\d+)', content)
        if match:
            minutes = float(match.group(1))
            seconds = float(match.group(2))
            total_seconds = minutes * 60 + seconds
            run_numbers.append(N)
            runtimes.append(total_seconds)
            print(f'Run {N}: {total_seconds} seconds')
        else:
            print(f'Runtime not found in {filename}')

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(run_numbers, runtimes, marker='o')
plt.title('Total Server Runtime vs. Number of Mid Section Repetitions')
plt.xlabel('Number of Mid Section Repetitions')
plt.ylabel('Total Server Runtime (seconds)')
plt.grid(True)
plt.xticks(range(1, 11))
plt.show()
