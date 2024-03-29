import time
import numpy as np
import matplotlib
matplotlib.use ('Agg')
import matplotlib.pyplot as plt
import pandas as pd

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

#from mne.viz.topomap import _prepare_topo_plot, plot_topomap
import mne
from mne.channels import read_layout

from mpl_toolkits.axes_grid1 import make_axes_locatable

def main():
    BoardShim.enable_dev_board_logger ()
    # use synthetic board for demo
    params = BrainFlowInputParams ()
    board = BoardShim (BoardIds.SYNTHETIC_BOARD.value, params)
    board.prepare_session ()
    board.start_stream ()
    time.sleep (10)
    data = board.get_board_data ()
    board.stop_stream ()
    board.release_session ()
    eeg_channels = BoardShim.get_eeg_channels (BoardIds.SYNTHETIC_BOARD.value)
    eeg_data = data[eeg_channels, :]
    eeg_data = eeg_data / 1000000 # BrainFlow returns uV, convert to V for MNE

    # Creating MNE objects from brainflow data arrays
    ch_types = ['eeg'] * len(eeg_channels)
    ch_names = BoardShim.get_eeg_names(BoardIds.SYNTHETIC_BOARD.value)
    print("channel names: ", ch_names)
    sfreq = BoardShim.get_sampling_rate(BoardIds.SYNTHETIC_BOARD.value)
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(eeg_data, info)
    # its time to plot something!
    raw.plot_psd()
    plt.savefig('psd.png')

    mne.export.export_raw("raw_data.eeg", raw, overwrite=True)
    np.savetxt("eeg_data.csv", eeg_data)

    raw.plot()
    plt.savefig('plot.png')

main()