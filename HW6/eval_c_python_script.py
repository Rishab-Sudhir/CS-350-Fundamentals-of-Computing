import re
import pandas as pd

# Define the alpha parameter for EWMA
alpha = 0.7

# Parse the server log file and extract request lengths
def parse_server_log(log_file):
    pattern = r"T\d+ R\d+:(?P<sent_ts>\d+\.\d+),(?P<img_op>\w+),\d+,\d+,\d+,(?P<receipt_ts>\d+\.\d+),(?P<start_ts>\d+\.\d+),(?P<compl_ts>\d+\.\d+)"
    data = []

    with open(log_file, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                img_op = match.group("img_op")
                sent_ts = float(match.group("sent_ts"))
                compl_ts = float(match.group("compl_ts"))
                request_length = compl_ts - sent_ts
                data.append((img_op, request_length))
    
    df = pd.DataFrame(data, columns=["img_op", "request_length"])
    return df

# Function to calculate EWMA and prediction error
def calculate_ewma_and_error(df):
    # Initialize dictionaries to store results
    estimators = {}  # To hold the EWMA estimator for each operation
    errors = {}      # To hold cumulative errors for each operation
    counts = {}      # To count occurrences of each operation
    
    for _, row in df.iterrows():
        img_op = row["img_op"]
        actual_length = row["request_length"]
        
        # Initialize EWMA estimator and error tracking for new operations
        if img_op not in estimators:
            estimators[img_op] = actual_length  # Initialize with first observed length
            errors[img_op] = 0.0
            counts[img_op] = 0
        
        # Calculate the prediction error
        prediction = estimators[img_op]
        error = abs(prediction - actual_length)
        
        # Update cumulative error and count
        errors[img_op] += error
        counts[img_op] += 1
        
        # Update the EWMA estimator
        estimators[img_op] = alpha * actual_length + (1 - alpha) * estimators[img_op]
    
    # Calculate average error for each operation
    avg_errors = {img_op: errors[img_op] / counts[img_op] for img_op in errors}
    return avg_errors

# Main function
def main():
    # Load and parse the RUN2 server log
    run2_log_file = "./eval_b_outputs/server_output_run2.log"  
    df = parse_server_log(run2_log_file)

    # Calculate the EWMA and prediction error for each operation
    avg_errors = calculate_ewma_and_error(df)

    # Display the results
    print("Average Prediction Error for Each Image Operation Type:")
    for img_op, avg_error in avg_errors.items():
        print(f"{img_op}: {avg_error:.6f} seconds")

# Run the main function
if __name__ == "__main__":
    main()
