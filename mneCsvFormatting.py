import pandas as pd
from mne import create_info
from mne.io import RawArray
import numpy as np
from mne.time_frequency import psd_array_welch

psd_df = pd.read_csv('eeg_data_modified.csv', names=['C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8', 'F5', 'F7', 'F3', 'F1', 'F2', 'F4', 'F6', 'F8'])

selected_channels = ['F7', 'F8', 'C3', 'C4']
psd_data = psd_df.loc[:, selected_channels].values.T  # transpose to have channels as rows

n_channels = len(selected_channels)
sfreq = 512  # sample rate in Hz
ch_names = selected_channels  # channel names are the selected channels

info = create_info(ch_names=ch_names, sfreq=sfreq, ch_types='eeg')
raw = RawArray(psd_data, info)

data = raw.get_data()

# Check if data contains NaN values or is empty
if np.isnan(data).any() or data.size == 0:
    print('Error: input data contains NaN values or is empty')
else:
    freqs, psd = psd_array_welch(data, sfreq=sfreq, fmin=0, fmax=50, n_fft=256, n_per_seg=512)

    spect = np.trapz(psd, x=freqs, axis=-1)

    print(spect)
