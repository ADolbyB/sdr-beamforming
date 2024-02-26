'''
    Peyton Adkins - Joel Brigida
    This is a Python script that reads data from specified binary folders.
    Using this script, it may be possible to exam the precise accuracy of the streams found in multiple Pluto SDR sources by plotting them along the same graph.

    The actual data for the stream output does not indicate any relatice domain. For this script, it is written to be displayed in the frequency domain to help aid in confirming frequency lock across multiple Pluto SDRs disciplined to a single external clock source.
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
# FILE_1 = "GNURadio/fileOutput"
FILE_1 = "GNURadio/plutoSDR/fileOutput/fileOutput"
# FILE_2 = "etc..."

'''Extract data as a complex64'''
# This is the stream output for basic signal processing in GNU Radio
f1 = np.fromfile(open(FILE_1), dtype=np.complex64)
# f2 = np.fromfile(open(FILE_2), dtype=np.complex64)

'''Visualizing the data in the frequency domain'''
SAMPLE_RATE = 2e6  # should be the same as it was in GNU Radio
NumSamples = f1.shape[0] # this ensures that it is relative to what is captured
fs = int(SAMPLE_RATE)                       # frequency size
ts = 1 / float(fs)                          # time size
xf = np.fft.fftfreq(NumSamples, ts)         # Assign frequency bins
xf = np.fft.fftshift(xf) / 1e6              # Convert to MHz

# '''Visualize Frequency Drift in the Time Domain'''
# signal, sample_rate = librosa.load(blues_1)
# max_time = signal.size / sample_rate

'''QT does not accept complex data, so we convert IQ samples to FFT'''
f1_db = dbfs(f1)
# f2 = dbfs(f2)

'''Create a main QT Window'''
win = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="File Output")
p1 = win.addPlot()
p1.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
p1.setLabel('left', 'Relative Gain', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
# p2 = win.addplot()
# p2.setLabel('bottom', 'Time', 'seconds', **{'color': '#FFF', 'size': '14pt'})
# p2.setLabel('left', 'Frequency', 'Hz', **{'color': '#FFF', 'size': '14pt'})

'''Per each data stream, create a curve on the same p1 plot'''
# Change the pen to any other color for clarity - 'b' is blue
curve1 = p1.plot(pen=pg.mkPen('r'))
curve1.setData(xf, f1_db)
label1 = pg.TextItem("Pluto 1 in BLUE")
label1.setParentItem(p1)
label1.setPos(65, 2)

# time_steps = np.linspace(0, max_time, signal.size)
# plt.figure()
# plt.plot(time_steps, signal)
# plt.xlabel("Time [s]")
# plt.ylabel("Amplitude")
# curve2 = p2.plot(pen=pg.mkPen('b'))
# curve2.setData(xf, f2)
# label2 = pg.TextItem("Pluto 2 in RED")
# label2.setParentItem(p1)
# label2.setPos(65, 24) # Change Y position for each label

# Keep QT Graph open until exiting
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        # QtGui.QApplication.instance().exec_() # 2023-12-01 JB: does not work (see next line)
        QtGui.QGuiApplication.instance().exec()