import time
import csv
from muselsl import stream, list_muses

# Connect to the first available Muse headset
muse = list_muses()[0]
stream_inlet = stream(muse['address'])

# Open a CSV file to store the data
csv_file = open("eeg_data.csv", "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["Timestamp", "Channel 1", "Channel 2", "Channel 3", "Channel 4"])

# Continuously read and store the EEG data in the CSV file
while True:
    try:
        # Read a sample of EEG data from the Muse headset
        sample, timestamp = stream_inlet.pull_sample()
        eeg_data = sample[:4]

        # Write the EEG data and timestamp to the CSV file
        writer.writerow([timestamp] + eeg_data)
        csv_file.flush()

        # Add a delay to avoid overloading the system
        time.sleep(0.01)
    except KeyboardInterrupt:
        break

# Close the CSV file and disconnect from the Muse headset
csv_file.close()
stream_inlet.close()
