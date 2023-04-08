import time
import numpy as np
import matplotlib
matplotlib.use ('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# # Import the Processing library
# import processing
# import processing.core.PApplet

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
    print(eeg_channels)
    muse_channel_names = ['F7', 'F8', 'C3', 'C4']
    eeg_data = data[eeg_channels, :]
    muse_data = eeg_data[[1, 2, 3, 4], :]
    eeg_data = eeg_data / 1000000 # BrainFlow returns uV, convert to V for MNE
    muse_data = muse_data / 1000000

    # Creating MNE objects from brainflow data arrays
    ch_types = ['eeg'] * len(eeg_channels)
    muse_ch_types = ['eeg'] * len(muse_data)
    ch_names = BoardShim.get_eeg_names(BoardIds.SYNTHETIC_BOARD.value)

    eegdf = pd.DataFrame(np.transpose(muse_data))
    eegdf.columns = muse_channel_names
    print(eegdf.shape)
    eegdf.to_csv('muse_out.csv',index=False)

    print("channel names: ", ch_names)
    sfreq = BoardShim.get_sampling_rate(BoardIds.SYNTHETIC_BOARD.value)
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    muse_info = mne.create_info(ch_names=muse_channel_names, sfreq=sfreq, ch_types=muse_ch_types)
    raw = mne.io.RawArray(eeg_data, info)
    muse_raw = mne.io.RawArray(muse_data, muse_info)


    # its time to plot something!
    raw.plot_psd()
    plt.savefig('psd.png')

    muse_raw.plot_psd(fmin=0, fmax=50)
    plt.savefig('psd_muse.png')

    mne.export.export_raw("raw_data.eeg", raw, overwrite=True)
    np.savetxt("eeg_data.csv", eeg_data)

    mne.export.export_raw("muse_raw_data.eeg", muse_raw, overwrite=True)
    np.savetxt("muse_eeg_data.csv", muse_data)

    raw.plot()
    plt.savefig('plot.png')



# # Create a class that inherits from PApplet
# class MySketch(processing.core.PApplet.PApplet):
  
#   # Setup function runs once at the beginning of the sketch
#   def setup(self):
#     # Set the size of the canvas
#     self.size(400, 400)
    
#   # Draw function runs repeatedly to draw the sketch
#   def draw(self):
#     # Get the current pixel value
#     pixel_val = self.noise(self.mouseX / float(self.width), self.mouseY / float(self.height))
    
#     # Map the pixel value to a color
#     color_val = self.map(pixel_val, 0, 1, 0, 255)
    
#     # Set the background color
#     self.background(0)
    
#     # Set the fill color based on the pixel value
#     if pixel_val > 0.5:
#       self.fill(255)
#     else:
#       self.fill(color_val)
    
#     # Draw a rectangle representing the pixel
#     self.rect(0, 0, self.width, self.height)

main()
