import pandas as pd
from mne import create_info
from mne.io import RawArray
import numpy as np
from scipy.signal import hann, butter, filtfilt

psd_df = pd.read_csv('eeg_data_modified.csv', header=None)
selected_channels = [8, 14, 0, 2]
psd_data = psd_df.iloc[selected_channels, :].values
psd_data = np.transpose(psd_data)
psd_data = np.transpose(psd_data, (1, 0))  # transpose to (4, n_samples)

n_channels = len(selected_channels)
sfreq = 512  # sample rate in Hz
ch_names = [str(channel) for channel in selected_channels] # channel names are the selected channels

info = create_info(ch_names=ch_names, sfreq=sfreq, ch_types='eeg')
raw = RawArray(psd_data, info)

data = raw.get_data()

# Define high-pass filter parameters
nyquist_freq = sfreq / 2
cutoff_freq = 1
filter_order = 4

# Create high-pass filter
b, a = butter(filter_order, cutoff_freq / nyquist_freq, btype='high')

# Apply filter to data
data_filt = filtfilt(b, a, data)

# Check if filtered data contains NaN values or is empty
if np.isnan(data_filt).any() or data_filt.size == 0:
    print('Error: filtered data contains NaN values or is empty')
else:
    window = hann(data_filt.shape[1])
    data_filt *= window.reshape((1, -1))
    freqs = np.linspace(0, sfreq/2, int(data_filt.shape[1]/2)+1)
    psd = np.abs(np.fft.fft(data_filt))**2
    psd = psd[:, :int(data_filt.shape[1]/2)+1]
    print(psd)

    spect = {}
    for i in range(n_channels):
        channel_data = psd[i]
        integral_values = []
        for j in range(0, len(channel_data), 256):
            slice_data = channel_data[j:j+256]
            integral = np.trapz(slice_data, x=freqs[j:j+256], axis=-1)
            integral_values.append(integral)
        spect[ch_names[i]] = integral_values
    print(spect)

    # Perform decimal normalization on spect dictionary
    for channel in ['8', '14', '0', '2']:
        channel_data = spect[channel]
        normalized_values = [float("{:.5f}".format(x / max(channel_data))) for x in channel_data]
        spect[channel] = normalized_values

    # Compute alpha to beta ratio
    alpha_beta = []
    for i in range(len(spect['8'])):
        alpha_beta.append(spect['8'][i] / spect['0'][i])
        alpha_beta.append(spect['14'][i] / spect['2'][i])
        alpha_beta.append(spect['8'][i] / spect['2'][i])
        alpha_beta.append(spect['14'][i] / spect['0'][i])

    print('Normalized spect: ', spect)
    print('Alpha to Beta Ratio: ', alpha_beta)
