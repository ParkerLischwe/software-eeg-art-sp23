import csv
import numpy as np

csv_file = 'eeg_data_modified.csv'

channels = [0, 2, 8, 14]

gamma_values = []
beta_values = []
alpha_values = []
theta_values = []

# Read CSV file and extract selected lines
with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    for i, row in enumerate(reader):
        if i in [0, 2, 8, 14]:
            channel_name = channels[i // 4]  # Use integer division to determine the channel name
            channel_values = np.array(row, dtype=float)
            # Apply Fast Fourier Transform (FFT) to the channel values
            fft_values = np.fft.fft(channel_values)
            # Take the absolute values of the FFT result to get the magnitude
            fft_magnitude = np.abs(fft_values)
            # Split the magnitude values into chunks of 256
            chunked_values = np.array_split(fft_magnitude, len(fft_magnitude) // 256)
            # Initialize sum of values in each wavelength band
            gamma_sum = 0
            beta_sum = 0
            alpha_sum = 0
            theta_sum = 0
            # Calculate sum of values in each wavelength band for each chunk
            for chunk in chunked_values:
                gamma_sum += np.sum(np.abs(chunk[32:100]))
                beta_sum += np.sum(np.abs(chunk[13:32]))
                alpha_sum += np.sum(np.abs(chunk[4:8]))
                theta_sum += np.sum(np.abs(chunk[0:4]))
            # Store integrated values in respective lists
            gamma_values.append(gamma_sum)
            beta_values.append(beta_sum)
            alpha_values.append(alpha_sum)
            theta_values.append(theta_sum)

output_file = 'alpha_beta_theta_gamma.csv'
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Channel', 'Wavelength', 'Value'])
    for i, channel in enumerate(channels):
        writer.writerow([channel, 'gamma', gamma_values[i]])
        writer.writerow([channel, 'beta', beta_values[i]])
        writer.writerow([channel, 'alpha', alpha_values[i]])
        writer.writerow([channel, 'theta', theta_values[i]])

print(f'Saved wavelength values to {output_file}.')
