'''
    Peyton Adkins - Joel Brigida
    This is a Python script that reads data from the specified binary folders of Rx1, Rx2, and Tx1 data sourced from a single Pluto SDR.
    The following script is derived from the logic of both Jon Kraft's work and Piotr Krysik's work in writing Python code for the Pluto SDR and for synchronizing multiple SDRs in GNU Radio.

    The actual data for the stream output does not indicate any relatice domain. For this script, it is written to be displayed in the time domain to help aid in confirming phase lock across multiple Rx nodes of a single Pluto SDR.
'''

import numpy as np
import pyqtgraph as pg  
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

'''Function to convert IQ samples to FFT plot, scaled in dBFS - Kraft'''
def dbfs(raw_data):                         
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20*np.log10(np.abs(s_shift)/(2**11))   # Pluto is a signed 12 bit ADC, so use 2^11 to convert to dBFS
    return s_dbfs

''' File names go here '''
FILE_Tx1 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/LocalPhaseSync/fileOutputTx1"
FILE_Rx1 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/LocalPhaseSync/fileOutputRx1"
FILE_Rx2 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/LocalPhaseSync/fileOutputRx2"

'''Extract data as a complex64'''
# This is the stream output for basic signal processing in GNU Radio
fTx1 = np.fromfile(open(FILE_Tx1), dtype=np.complex64)
fRx1 = np.fromfile(open(FILE_Rx1), dtype=np.complex64)
fRx2 = np.fromfile(open(FILE_Rx2), dtype=np.complex64)

# Reshape the Tx data to fit that of the Rx data (Rx1 and Rx2 are of same shape)
fTx1 = np.resize(fTx1, fRx1.shape)

'''Create a main QT Window'''
win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Raw File Output")

'''Visualizing the raw data'''
DOMAIN = "time" # freq or time
SAMPLE_RATE = 2e6  # should be the same as it was in GNU Radio
NUM_SAMPLES = fRx1.shape[0] # this ensures that it is relative to what is captured

if DOMAIN == "freq":
    # # # Frequency Domain

    fs = int(SAMPLE_RATE)                       # frequency size
    ts = 1 / float(fs)                          # time size
    xf = np.fft.fftfreq(NUM_SAMPLES, ts)         # Assign frequency bins
    xf = np.fft.fftshift(xf) / 1e6              # Convert to MHz

    # QT does not accept complex data, so we convert IQ samples to FFT
    fTx1_db = dbfs(fTx1)
    fRx1_db = dbfs(fRx1)
    fRx2_db = dbfs(fRx2)

    # Visualize data
    p1 = win_raw.addPlot()
    p1.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p1.setLabel('left', 'Relative Gain', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    # Change the pen to any other color for clarity - 'b' is blue
    curve1 = p1.plot(pen=pg.mkPen('b'))
    curve1.setData(xf, fRx1_db)
    label1 = pg.TextItem("Rx1 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p1.plot(pen=pg.mkPen('r'))
    curve2.setData(xf, fRx2_db)
    label2 = pg.TextItem("Rx2 in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24)
    curve3 = p1.plot(pen=pg.mkPen('g'))
    curve3.setData(xf, fTx1_db)
    label3 = pg.TextItem("Tx1 in GREEN")
    label3.setParentItem(p1)
    label3.setPos(65, 46) # Change Y position for each label

elif DOMAIN == "time":
    # # # Time Domain

    # QT does not accept complex data, so we separate IQ samples by their real values from their imaginary values
    fTx1_r = np.real(fTx1)
    fRx1_r = np.real(fRx1)
    fRx2_r = np.real(fRx2)

    # Time axis
    taxs = np.arange(NUM_SAMPLES)/SAMPLE_RATE
    
    # Visualize data
    p1 = win_raw.addPlot()
    p1.setLabel('bottom', 'Time', 'sec', **{'color': '#FFF', 'size': '14pt'})
    p1.setLabel('left', 'Amplitude', **{'color': '#FFF', 'size': '14pt'})
    p1.setYRange(-2, 2, padding=0)
    # p1.setXRange(0, 0.25, padding=0)
    # Change the pen to any other color for clarity - 'b' is blue
    curve1 = p1.plot(pen=pg.mkPen('b'))
    curve1.setData(taxs, fRx1_r)
    label1 = pg.TextItem("Rx1 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p1.plot(pen=pg.mkPen('r'))
    curve2.setData(taxs, fRx2_r)
    label2 = pg.TextItem("Rx2 in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24)
    curve3 = p1.plot(pen=pg.mkPen('g'))
    curve3.setData(taxs, fTx1_r)
    label3 = pg.TextItem("Tx1 in GREEN")
    label3.setParentItem(p1)
    label3.setPos(65, 46) # Change Y position for each label

else: 
    raise ValueError(print("Not a valid domain type."))

# Keep QT Graph open until exiting
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        # QtGui.QApplication.instance().exec_() # 2023-12-01 JB: does not work (see next line)
        QtGui.QGuiApplication.instance().exec()