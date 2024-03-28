'''
Peyton Adkins - Joel Brigida
This is a Python script that reads data from the specified binary folders of Rx1 and Rx2 data sourced from a single 
Pluto SDR. This script is derived from the logic of both Jon Kraft's work and Piotr Krysik's work in writing Python 
code for the Pluto SDR and for synchronizing multiple SDRs in GNU Radio.

The actual data for the stream output does not indicate any relatice domain. For this script, it is written to be 
displayed in the time domain to help aid in confirming phase lock across multiple Rx nodes of a single Pluto SDR.
'''

import numpy as np
import pylab as pl
import pyqtgraph as pg  
from pyqtgraph.Qt import QtCore, QtGui

''' Function to convert IQ samples to FFT plot, scaled in dBFS - Kraft '''
def dbfs(raw_data):                         
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20 * np.log10(np.abs(s_shift) / (2**11))   # Pluto is a signed 12 bit ADC, so use 2^11 to convert to dBFS
    return s_dbfs

''' IQ Files to Read: '''
FILE_P2 = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP2.iq"
FILE_P3 = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP3.iq"
FILE_P4 = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP4.iq"
FILE_P5 = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP5.iq"

''' Extract data as a complex64 '''
# This is the stream output for basic signal processing in GNU Radio
fP2 = pl.fromfile(open(FILE_P2), dtype=np.complex64)
fP3 = pl.fromfile(open(FILE_P3), dtype=np.complex64)
fP3 = pl.resize(fP3, fP2.shape)
fP4 = pl.fromfile(open(FILE_P4), dtype=np.complex64)
fP4 = pl.resize(fP4, fP2.shape)
fP5 = pl.fromfile(open(FILE_P5), dtype=np.complex64)
fP5 = pl.resize(fP5, fP2.shape)

GRAPHS = "all" # stack, raster or all
DOMAIN = "time" # freq, time or all
SAMPLE_RATE = 2e6  # should be the same as it was in GNU Radio
NUM_SAMPLES = fP2.shape[0] # this ensures that it is relative to what is captured

''' Visualizing raw data '''
if DOMAIN == "freq" and GRAPHS == "stack":
    ## Frequency Domain
    # 1 window with a single graph with all plots stacked on top of each other

    ''' Create a main QT Window '''
    win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Frequency Domain Sample: Stacked")

    fs = int(SAMPLE_RATE)                       # frequency size
    ts = 1 / float(fs)                          # time size
    xf = np.fft.fftfreq(NUM_SAMPLES, ts)        # Assign frequency bins
    xf = np.fft.fftshift(xf) / 1e6              # Convert to MHz

    # QT does not accept complex data, so we convert IQ samples to FFT
    fRx1_db = dbfs(fP2)
    fRx2_db = dbfs(fP3)
    fRx3_db = dbfs(fP4)
    fRx4_db = dbfs(fP5)

    # Visualize data
    p1 = win_raw.addPlot()
    p1.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p1.setLabel('left', 'Relative Gain', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    curve1 = p1.plot(pen=pg.mkPen('b'))
    curve1.setData(xf, fRx1_db)
    label1 = pg.TextItem("P2.1 Rx1 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p1.plot(pen=pg.mkPen('r'))
    curve2.setData(xf, fRx2_db)
    label2 = pg.TextItem("P2.1 Rx2 in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24) # Change Y position for each label
    curve3 = p1.plot(pen=pg.mkPen('g'))
    curve3.setData(xf, fRx3_db)
    label3 = pg.TextItem("P3.1 Rx1 in GREEN")
    label3.setParentItem(p1)
    label3.setPos(65, 46) # Change Y position for each label
    curve4 = p1.plot(pen=pg.mkPen('y'))
    curve4.setData(xf, fRx4_db)
    label4 = pg.TextItem("P3.1 Rx2 in YELLOW")
    label4.setParentItem(p1)
    label4.setPos(65, 68) # Change Y position for each label

elif DOMAIN == "freq" and GRAPHS == "raster":
    ## Frequency Domain
    # 1 window with different graph plots for each channel
    ''' Create a main QT Window '''
    win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Frequency Domain Sample: Raster")

    fs = int(SAMPLE_RATE)                       # frequency size
    ts = 1 / float(fs)                          # time size
    xf = np.fft.fftfreq(NUM_SAMPLES, ts)        # Assign frequency bins
    xf = np.fft.fftshift(xf) / 1e6              # Convert to MHz

    # QT does not accept complex data, so we convert IQ samples to FFT
    fRx1_db = dbfs(fP2)
    fRx2_db = dbfs(fP3)
    fRx3_db = dbfs(fP4)
    fRx4_db = dbfs(fP5)

    # Visualize data
    p1 = win_raw.addPlot()
    p1.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p1.setLabel('left', 'Relative Gain - Rx1', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p2 = win_raw.addPlot()
    p2.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p2.setLabel('left', 'Relative Gain - Rx2', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p3 = win_raw.addPlot()
    p3.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p3.setLabel('left', 'Relative Gain - Rx3', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p4 = win_raw.addPlot()
    p4.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p4.setLabel('left', 'Relative Gain - Rx4', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    curve1 = p1.plot(pen=pg.mkPen('b'))
    curve1.setData(xf, fRx1_db)
    label1 = pg.TextItem("P2.1 Rx1 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p2.plot(pen=pg.mkPen('r'))
    curve2.setData(xf, fRx2_db)
    label2 = pg.TextItem("P2.1 Rx2 in RED")
    label2.setParentItem(p2)
    label2.setPos(65, 2) # Change Y position for each label
    curve3 = p3.plot(pen=pg.mkPen('g'))
    curve3.setData(xf, fRx3_db)
    label3 = pg.TextItem("P3.1 Rx1 in GREEN")
    label3.setParentItem(p3)
    label3.setPos(65, 2) # Change Y position for each label
    curve4 = p4.plot(pen=pg.mkPen('y'))
    curve4.setData(xf, fRx4_db)
    label4 = pg.TextItem("P3.1 Rx2 in YELLOW")
    label4.setParentItem(p4)
    label4.setPos(65, 2) # Change Y position for each label

elif DOMAIN == "freq" and GRAPHS == "all":
    ## Frequency Domain
    # 2 windows: 1 with different graph plots for each channel & 1 with channels separated
    ''' Create 2 QT Windows '''
    win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Frequency Domain Sample: Stacked")
    win_raw2 = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Frequency Domain Sample: Raster")

    fs = int(SAMPLE_RATE)                       # frequency size
    ts = 1 / float(fs)                          # time size
    xf = np.fft.fftfreq(NUM_SAMPLES, ts)        # Assign frequency bins
    xf = np.fft.fftshift(xf) / 1e6              # Convert to MHz

    # QT does not accept complex data, so we convert IQ samples to FFT
    fRx1_db = dbfs(fP2)
    fRx2_db = dbfs(fP3)
    fRx3_db = dbfs(fP4)
    fRx4_db = dbfs(fP5)
    
    # Visualize data: Window 1 (Stacked)
    p1 = win_raw.addPlot()
    p1.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p1.setLabel('left', 'Relative Gain', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    curve1 = p1.plot(pen=pg.mkPen('b'))
    curve1.setData(xf, fRx1_db)
    label1 = pg.TextItem("P2.1 Rx1 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p1.plot(pen=pg.mkPen('r'))
    curve2.setData(xf, fRx2_db)
    label2 = pg.TextItem("P2.1 Rx2 in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24) # Change Y position for each label
    curve3 = p1.plot(pen=pg.mkPen('g'))
    curve3.setData(xf, fRx3_db)
    label3 = pg.TextItem("P3.1 Rx1 in GREEN")
    label3.setParentItem(p1)
    label3.setPos(65, 46) # Change Y position for each label
    curve4 = p1.plot(pen=pg.mkPen('y'))
    curve4.setData(xf, fRx4_db)
    label4 = pg.TextItem("P3.1 Rx2 in YELLOW")
    label4.setParentItem(p1)
    label4.setPos(65, 68) # Change Y position for each label
    
    # Visualize data: Window 2 (Raster)
    p2 = win_raw2.addPlot()
    p2.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p2.setLabel('left', 'Relative Gain - Rx1', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p3 = win_raw2.addPlot()
    p3.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p3.setLabel('left', 'Relative Gain - Rx2', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p4 = win_raw2.addPlot()
    p4.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p4.setLabel('left', 'Relative Gain - Rx3', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p5 = win_raw2.addPlot()
    p5.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p5.setLabel('left', 'Relative Gain - Rx4', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    curve1a = p2.plot(pen=pg.mkPen('b'))
    curve1a.setData(xf, fRx1_db)
    label1a = pg.TextItem("P2.1 Rx1 in BLUE")
    label1a.setParentItem(p2)
    label1a.setPos(65, 2)
    curve2a = p3.plot(pen=pg.mkPen('r'))
    curve2a.setData(xf, fRx2_db)
    label2a = pg.TextItem("P2.1 Rx2 in RED")
    label2a.setParentItem(p3)
    label2a.setPos(65, 2) # Change Y position for each label
    curve3a = p4.plot(pen=pg.mkPen('g'))
    curve3a.setData(xf, fRx3_db)
    label3a = pg.TextItem("P3.1 Rx1 in GREEN")
    label3a.setParentItem(p4)
    label3a.setPos(65, 2) # Change Y position for each label
    curve4a = p5.plot(pen=pg.mkPen('y'))
    curve4a.setData(xf, fRx4_db)
    label4a = pg.TextItem("P3.1 Rx2 in YELLOW")
    label4a.setParentItem(p5)
    label4a.setPos(65, 2) # Change Y position for each label

elif DOMAIN == "time":
    ## Time Domain
    ''' Create a main QT Window '''
    win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Time Domain Sample Output")
    
    # QT does not accept complex data, so we separate IQ samples by their real values from their imaginary values
    fRx1_r = np.real(fP2)
    fRx2_r = np.real(fP3)
    fRx3_r = np.real(fP4)
    fRx4_r = np.real(fP5)

    # Time axis
    t_ax = np.arange(NUM_SAMPLES) / SAMPLE_RATE
    
    # Visualize data
    p1 = win_raw.addPlot()
    p1.setLabel('bottom', 'Time', 'sec', **{'color': '#FFF', 'size': '14pt'})
    p1.setLabel('left', 'Amplitude', **{'color': '#FFF', 'size': '14pt'})
    p1.setYRange(-1, 1, padding=0)

    # Change the pen for clarity - 'b' is blue
    curve1 = p1.plot(pen=pg.mkPen('b'))
    curve1.setData(t_ax, fRx1_r)
    label1 = pg.TextItem("P2.1 Rx1 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p1.plot(pen=pg.mkPen('r'))
    curve2.setData(t_ax, fRx2_r)
    label2 = pg.TextItem("P2.1 Rx2 in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24) # Change Y position for each label
    curve3 = p1.plot(pen=pg.mkPen('g'))
    curve3.setData(t_ax, fRx3_r)
    label3 = pg.TextItem("P3.1 Rx1 in GREEN")
    label3.setParentItem(p1)
    label3.setPos(65, 46) # Change Y position for each label
    curve4 = p1.plot(pen=pg.mkPen('y'))
    curve4.setData(t_ax, fRx4_r)
    label4 = pg.TextItem("P3.1 Rx2 in YELLOW")
    label4.setParentItem(p1)
    label4.setPos(65, 68) # Change Y position for each label

elif DOMAIN == "all":

    # 2 windows: 1 with different graph plots for each channel & 1 with channels separated
    ''' Create 3 QT Windows '''
    win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Time Domain Sample Output")
    win_raw2 = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Frequency Domain Sample: Stacked")
    win_raw3 = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Frequency Domain Sample: Raster")
    
    ''' Time Domain Display: All Channels on a single plot '''
    # QT does not accept complex data, so we separate IQ samples by their real values from their imaginary values
    # Real Data is for the Time Display
    fRx1_r = np.real(fP2)
    fRx2_r = np.real(fP3)
    fRx3_r = np.real(fP4)
    fRx4_r = np.real(fP5)

    # Time axis
    t_ax = np.arange(NUM_SAMPLES) / SAMPLE_RATE
    
    # Visualize data
    p1_t = win_raw.addPlot()
    p1_t.setLabel('bottom', 'Time', 'sec', **{'color': '#FFF', 'size': '14pt'})
    p1_t.setLabel('left', 'Amplitude', **{'color': '#FFF', 'size': '14pt'})
    p1_t.setYRange(-1, 1, padding=0)

    # Change the pen for clarity - 'b' is blue
    curve1_t = p1_t.plot(pen=pg.mkPen('b'))
    curve1_t.setData(t_ax, fRx1_r)
    label1_t = pg.TextItem("P2.1 Rx1 in BLUE")
    label1_t.setParentItem(p1_t)
    label1_t.setPos(65, 2)
    curve2_t = p1_t.plot(pen=pg.mkPen('r'))
    curve2_t.setData(t_ax, fRx2_r)
    label2_t = pg.TextItem("P2.1 Rx2 in RED")
    label2_t.setParentItem(p1_t)
    label2_t.setPos(65, 24) # Change Y position for each label
    curve3_t = p1_t.plot(pen=pg.mkPen('g'))
    curve3_t.setData(t_ax, fRx3_r)
    label3_t = pg.TextItem("P3.1 Rx1 in GREEN")
    label3_t.setParentItem(p1_t)
    label3_t.setPos(65, 46) # Change Y position for each label
    curve4_t = p1_t.plot(pen=pg.mkPen('y'))
    curve4_t.setData(t_ax, fRx4_r)
    label4_t = pg.TextItem("P3.1 Rx2 in YELLOW")
    label4_t.setParentItem(p1_t)
    label4_t.setPos(65, 68) # Change Y position for each label

    ''' Freq Domain Display: 2 Windows '''
    fs = int(SAMPLE_RATE)                       # frequency size
    ts = 1 / float(fs)                          # time size
    xf = np.fft.fftfreq(NUM_SAMPLES, ts)        # Assign frequency bins
    xf = np.fft.fftshift(xf) / 1e6              # Convert to MHz

    # QT does not accept complex data, so we convert IQ samples to FFT
    fRx1_db = dbfs(fP2)
    fRx2_db = dbfs(fP3)
    fRx3_db = dbfs(fP4)
    fRx4_db = dbfs(fP5)
    
    # Visualize data: Window 1 (Stacked)
    p1 = win_raw2.addPlot()
    p1.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p1.setLabel('left', 'Relative Gain', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    curve1 = p1.plot(pen=pg.mkPen('b'))
    curve1.setData(xf, fRx1_db)
    label1 = pg.TextItem("P2.1 Rx1 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p1.plot(pen=pg.mkPen('r'))
    curve2.setData(xf, fRx2_db)
    label2 = pg.TextItem("P2.1 Rx2 in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24) # Change Y position for each label
    curve3 = p1.plot(pen=pg.mkPen('g'))
    curve3.setData(xf, fRx3_db)
    label3 = pg.TextItem("P3.1 Rx1 in GREEN")
    label3.setParentItem(p1)
    label3.setPos(65, 46) # Change Y position for each label
    curve4 = p1.plot(pen=pg.mkPen('y'))
    curve4.setData(xf, fRx4_db)
    label4 = pg.TextItem("P3.1 Rx2 in YELLOW")
    label4.setParentItem(p1)
    label4.setPos(65, 68) # Change Y position for each label
    
    # Visualize data: Window 2 (Raster)
    p2 = win_raw3.addPlot()
    p2.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p2.setLabel('left', 'Relative Gain - Rx1', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p3 = win_raw3.addPlot()
    p3.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p3.setLabel('left', 'Relative Gain - Rx2', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p4 = win_raw3.addPlot()
    p4.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p4.setLabel('left', 'Relative Gain - Rx3', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p5 = win_raw3.addPlot()
    p5.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p5.setLabel('left', 'Relative Gain - Rx4', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    curve1a = p2.plot(pen=pg.mkPen('b'))
    curve1a.setData(xf, fRx1_db)
    label1a = pg.TextItem("P2.1 Rx1 in BLUE")
    label1a.setParentItem(p2)
    label1a.setPos(65, 2)
    curve2a = p3.plot(pen=pg.mkPen('r'))
    curve2a.setData(xf, fRx2_db)
    label2a = pg.TextItem("P2.1 Rx2 in RED")
    label2a.setParentItem(p3)
    label2a.setPos(65, 2) # Change Y position for each label
    curve3a = p4.plot(pen=pg.mkPen('g'))
    curve3a.setData(xf, fRx3_db)
    label3a = pg.TextItem("P3.1 Rx1 in GREEN")
    label3a.setParentItem(p4)
    label3a.setPos(65, 2) # Change Y position for each label
    curve4a = p5.plot(pen=pg.mkPen('y'))
    curve4a.setData(xf, fRx4_db)
    label4a = pg.TextItem("P3.1 Rx2 in YELLOW")
    label4a.setParentItem(p5)
    label4a.setPos(65, 2) # Change Y position for each label
    
else: 
    raise ValueError(print("Not a valid domain/graph type."))

# Keep QT Graph open until exiting
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec()