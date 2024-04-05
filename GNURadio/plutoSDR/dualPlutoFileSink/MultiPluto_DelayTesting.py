'''
Peyton Adkins - Joel Brigida
This is a Python script that reads data from the specified binary folders of Rx1 and Rx2 data sourced from a single 
Pluto SDR. This script is derived from the logic of both Jon Kraft's work and Piotr Krysik's work in writing Python 
code for the Pluto SDR and for synchronizing multiple SDRs in GNU Radio.

The actual data for the stream output does not indicate any relatice domain. For this script, it is written to be 
displayed in the time domain to help aid in confirming phase lock across multiple Rx nodes of a single Pluto SDR.
'''

import math
import numpy as np
import pylab as pl
import pyqtgraph as pg  
from pyqtgraph.Qt import QtCore, QtGui
import struct

'''Function for trimming ndarray data'''
def trimDelay(input, delayDelta):
    # output = input
    # num_output = input.shape[0]
    # num_to_copy = max(0, num_output - delayDelta)
    # num_adj = min(delayDelta, num_output)
    # for i in range(num_output):
    #     iptr = input[i]
    #     optr = output[i]
    #     optr[:num_to_copy]
    # std::memcpy(input)
    input = np.pad(input, (0, delayDelta), 'constant', constant_values=(0))
    input = input[delayDelta:]
    return input

'''Function for padding ndarray data'''
def padDelay(input, delayDelta):
    length = len(input)
    input = np.pad(input, (delayDelta, 0), 'constant', constant_values=(0))
    input = input[:length]
    return input

'''Function for cross-correlation - Krysik'''
def xcorrelate(X, Y, maxlag):
    N = max(len(X), len(Y))
    N_nextpow2 = math.ceil(math.log(N + maxlag, 2))
    M = 2**N_nextpow2
    if len(X) < M:
        postpad_X = int(M - len(X) - maxlag)
    else: 
        postpad_X = 0

    if len(Y) < M:
        postpad_Y = int(M - len(Y))
    else:
        postpad_Y = 0
        
    pre  = pl.fft( np.pad(X, (maxlag,postpad_X), 'constant', constant_values=(0, 0)) )
    post = pl.fft( np.pad(Y, (0,postpad_Y), 'constant', constant_values=(0, 0)) )
    cor  = pl.ifft( pre * np.conj(post) )
    R = cor[0 : 2*maxlag]
    return R

'''Function for computing and finding delays - Krysik'''
def compute_and_set_delay(ref_data, Rx_data, Rx_name, samp_rate):

    result_corr = xcorrelate(ref_data, Rx_data,int(len(ref_data) / 2))
    max_position = np.argmax(abs(result_corr))
    delay = len(result_corr) / 2 - max_position

    phase_diff = result_corr[max_position] / np.sqrt(np.mean(np.real(Rx_data)**2 + np.imag(Rx_data)**2))
    # phase_diff = sqrt(var(ref_data)/var(Rx_data))*(exp(1j*angle(phase_diff)))
    phase_diff = np.angle(phase_diff) / np.pi * 180

    print ("Delay of ", Rx_name, ": ", delay,' | Phase Diff: ', phase_diff, " [deg]")

    # Set phase amplitude correction
    # INSERT
    # phase_amplitude_correction = sqrt(var(ref_data)/var(Rx_data))*(exp(1j*angle(phase_amplitude_correction)))

    trim = Rx_data

    # Set delay     
    if delay < 0:
        trim = padDelay(Rx_data, int(-delay)) # *samp_rate
    elif delay > 0:
        trim = trimDelay(Rx_data, int(delay)) # *samp_rate

    # return Rx_data * np.exp(1j*np.deg2rad(phase_diff))
    return trim * np.sqrt(np.var(ref_data) / np.var(Rx_data)) * (np.exp(1j * np.deg2rad(phase_diff)))

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
# JOEL
# FILE_TX = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputTX.iq"
# FILE_P2 = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP2.iq"
# FILE_P3 = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP3.iq"
# FILE_P4 = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP4.iq"
# FILE_P5 = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP5.iq"
# PEYTON
FILE_TX = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputTX.iq"
FILE_P2 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP2.iq"
FILE_P3 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP3.iq"
FILE_P4 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP4.iq"
FILE_P5 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP5.iq"

''' Extract data as a complex64 '''
# This is the stream output for basic signal processing in GNU Radio
fP2 = pl.fromfile(open(FILE_P2), dtype=np.complex64)
fP3 = pl.fromfile(open(FILE_P3), dtype=np.complex64)
print(f'Shape of fP2[0]: {fP2.shape[0]}')
fP3 = pl.resize(fP3, fP2.shape)
print(f'Shape of fP3[0]: {fP3.shape[0]}')
fP4 = pl.fromfile(open(FILE_P4), dtype=np.complex64)
print(f'Shape of fP4[0]: {fP4.shape[0]}')
fP4 = pl.resize(fP4, fP2.shape)
fP5 = pl.fromfile(open(FILE_P5), dtype=np.complex64)
print(f'Shape of fP5[0]: {fP5.shape[0]}')
fP5 = pl.resize(fP5, fP2.shape)
fTX = pl.fromfile(open(FILE_TX), dtype=np.complex64)
print(f'Shape of fTX[0]: {fTX.shape[0]}')
fTX = pl.resize(fTX, fP2.shape)

GRAPHS = "all" # stack, raster or all
DOMAIN = "all" # freq, time or all
SAMPLE_RATE = 2e6  # should be the same as it was in GNU Radio
NUM_SAMPLES = fP2.shape[0] # this ensures that it is relative to what is captured

'''Cross-Correlation and Delay Values'''
DfP3 = compute_and_set_delay(fP2, fP3, "Pluto 2.1 Rx1", SAMPLE_RATE)
nil = compute_and_set_delay(fP2, DfP3, "Pluto 2.1 Rx1", SAMPLE_RATE)
# DfP5 = compute_and_set_delay(fP4, fP5, "Pluto 5.1 Rx1", SAMPLE_RATE)
# nil = compute_and_set_delay(fP4, DfP5, "Pluto 5.1 Rx1", SAMPLE_RATE)
# DfP5 = compute_and_set_delay(fP2, fP5, "Pluto 5.1 Rx1", SAMPLE_RATE)
# nil = compute_and_set_delay(fP2, DfP5, "Pluto 5.1 Rx1", SAMPLE_RATE)
# DfP4 = compute_and_set_delay(fP2, fP4, "Pluto 5.1 Rx0", SAMPLE_RATE)
# nil = compute_and_set_delay(fP2, DfP4, "Pluto 5.1 Rx0", SAMPLE_RATE)
DfP4 = compute_and_set_delay(fP2, fP4, "Pluto 5.1 Rx0", SAMPLE_RATE)
nil = compute_and_set_delay(fP2, DfP4, "Pluto 5.1 Rx0", SAMPLE_RATE)
DfP5 = compute_and_set_delay(fP2, fP5, "Pluto 5.1 Rx1", SAMPLE_RATE)
nil = compute_and_set_delay(fP2, DfP5, "Pluto 5.1 Rx1", SAMPLE_RATE)

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
    fTX_db = dbfs(fTX)

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
    curve5 = p1.plot(pen=pg.mkPen('o'))
    curve5.setData(xf, fRx4_db)
    label5 = pg.TextItem("tx Data in ORANGE")
    label5.setParentItem(p1)
    label5.setPos(65, 80) # Change Y position for each label

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
    fTX_db = dbfs(fTX)

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
    p5 = win_raw.addPlot()
    p5.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p5.setLabel('left', 'Relative Gain - TX', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    curve1 = p1.plot(pen=pg.mkPen('b'))
    curve1.setData(xf, fRx1_db)
    label1 = pg.TextItem("P2.1 Rx0 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p2.plot(pen=pg.mkPen('r'))
    curve2.setData(xf, fRx2_db)
    label2 = pg.TextItem("P2.1 Rx1 in RED")
    label2.setParentItem(p2)
    label2.setPos(65, 2) # Change Y position for each label
    curve3 = p3.plot(pen=pg.mkPen('g'))
    curve3.setData(xf, fRx3_db)
    label3 = pg.TextItem("P3.1 Rx0 in GREEN")
    label3.setParentItem(p3)
    label3.setPos(65, 2) # Change Y position for each label
    curve4 = p4.plot(pen=pg.mkPen('y'))
    curve4.setData(xf, fRx4_db)
    label4 = pg.TextItem("P3.1 Rx1 in YELLOW")
    label4.setParentItem(p4)
    label4.setPos(65, 2) # Change Y position for each label
    curve5 = p5.plot(pen=pg.mkPen('o'))
    curve5.setData(xf, fRx4_db)
    label5 = pg.TextItem("tx Data in ORANGE")
    label5.setParentItem(p1)
    label5.setPos(65, 80) # Change Y position for each label

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
    label1 = pg.TextItem("P2.1 Rx0 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p1.plot(pen=pg.mkPen('r'))
    curve2.setData(xf, fRx2_db)
    label2 = pg.TextItem("P2.1 Rx1 in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24) # Change Y position for each label
    curve3 = p1.plot(pen=pg.mkPen('g'))
    curve3.setData(xf, fRx3_db)
    label3 = pg.TextItem("P5.1 Rx0 in GREEN")
    label3.setParentItem(p1)
    label3.setPos(65, 46) # Change Y position for each label
    curve4 = p1.plot(pen=pg.mkPen('y'))
    curve4.setData(xf, fRx4_db)
    label4 = pg.TextItem("P5.1 Rx1 in YELLOW")
    label4.setParentItem(p1)
    label4.setPos(65, 68) # Change Y position for each label
    
    # Visualize data: Window 2 (Raster)
    p2 = win_raw2.addPlot()
    p2.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p2.setLabel('left', 'Relative Gain - P2.1 Rx0', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p3 = win_raw2.addPlot()
    p3.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p3.setLabel('left', 'Relative Gain - P2.1 Rx1', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p4 = win_raw2.addPlot()
    p4.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p4.setLabel('left', 'Relative Gain - P5.1 Rx0', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    p5 = win_raw2.addPlot()
    p5.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    p5.setLabel('left', 'Relative Gain - P5.1 Rx1', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    curve1a = p2.plot(pen=pg.mkPen('b'))
    curve1a.setData(xf, fRx1_db)
    label1a = pg.TextItem("P2.1 Rx0 in BLUE")
    label1a.setParentItem(p2)
    label1a.setPos(65, 2)
    curve2a = p3.plot(pen=pg.mkPen('r'))
    curve2a.setData(xf, fRx2_db)
    label2a = pg.TextItem("P2.1 Rx1 in RED")
    label2a.setParentItem(p3)
    label2a.setPos(65, 2) # Change Y position for each label
    curve3a = p4.plot(pen=pg.mkPen('g'))
    curve3a.setData(xf, fRx3_db)
    label3a = pg.TextItem("P5.1 Rx0 in GREEN")
    label3a.setParentItem(p4)
    label3a.setPos(65, 2) # Change Y position for each label
    curve4a = p5.plot(pen=pg.mkPen('y'))
    curve4a.setData(xf, fRx4_db)
    label4a = pg.TextItem("P5.1 Rx1 in YELLOW")
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
    label1 = pg.TextItem("P2.1 Rx0 in BLUE")
    label1.setParentItem(p1)
    label1.setPos(65, 2)
    curve2 = p1.plot(pen=pg.mkPen('r'))
    curve2.setData(t_ax, fRx2_r)
    label2 = pg.TextItem("P2.1 Rx1 in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24) # Change Y position for each label
    curve3 = p1.plot(pen=pg.mkPen('g'))
    curve3.setData(t_ax, fRx3_r)
    label3 = pg.TextItem("P5.1 Rx0 in GREEN")
    label3.setParentItem(p1)
    label3.setPos(65, 46) # Change Y position for each label
    curve4 = p1.plot(pen=pg.mkPen('y'))
    curve4.setData(t_ax, fRx4_r)
    label4 = pg.TextItem("P5.1 Rx1 in YELLOW")
    label4.setParentItem(p1)
    label4.setPos(65, 68) # Change Y position for each label

elif DOMAIN == "all":

    # 2 windows: 1 with different graph plots for each channel & 1 with channels separated
    ''' Create 3 QT Windows '''
    win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Time Domain Sample Output")
    # win_raw2 = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Frequency Domain Sample: Stacked")
    # win_raw3 = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Frequency Domain Sample: Raster")
    # win_raw4 = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Time Domain TX Data")
    win_cross = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Time Domain Sample Output [CORRECTED]")
    
    ''' Time Domain Display: All Channels on a single plot '''
    # QT does not accept complex data, so we separate IQ samples by their real values from their imaginary values
    # Real Data is for the Time Display
    fRx1_r = np.real(fP2)
    fRx2_r = np.real(fP3)
    fRx3_r = np.real(fP4)
    fRx4_r = np.real(fP5)
    fTX_r = np.real(fTX)
    #
    DfP3_r = np.real(DfP3)
    DfP4_r = np.real(DfP4)
    # DfP4_r = np.real(fP4)
    DfP5_r = np.real(DfP5)

    # Time axis
    t_ax = np.arange(NUM_SAMPLES) / SAMPLE_RATE
    
    # Visualize data
    p1_t = win_raw.addPlot()
    p1_t.setLabel('bottom', 'Time', 'sec', **{'color': '#FFF', 'size': '14pt'})
    p1_t.setLabel('left', 'Amplitude', **{'color': '#FFF', 'size': '14pt'})
    p1_t.setYRange(-1, 1, padding=0)

    # p2_t = win_raw4.addPlot()
    # p2_t.setLabel('bottom', 'Time', 'sec', **{'color': '#FFF', 'size': '14pt'})
    # p2_t.setLabel('left', 'Amplitude', **{'color': '#FFF', 'size': '14pt'})
    # p2_t.setYRange(-1, 1, padding=0)

    p3_t = win_cross.addPlot()
    p3_t.setLabel('bottom', 'Time', 'sec', **{'color': '#FFF', 'size': '14pt'})
    p3_t.setLabel('left', 'Amplitude', **{'color': '#FFF', 'size': '14pt'})
    p3_t.setYRange(-1, 1, padding=0)

    # RAW TIME DATA
    # Change the pen for clarity - 'b' is blue
    curve1_t = p1_t.plot(pen=pg.mkPen('b'))
    curve1_t.setData(t_ax, fRx1_r)
    label1_t = pg.TextItem("P2.1 Rx0 in BLUE")
    label1_t.setParentItem(p1_t)
    label1_t.setPos(65, 2)
    curve2_t = p1_t.plot(pen=pg.mkPen('r'))
    curve2_t.setData(t_ax, fRx2_r)
    label2_t = pg.TextItem("P2.1 Rx1 in RED")
    label2_t.setParentItem(p1_t)
    label2_t.setPos(65, 24) # Change Y position for each label
    curve3_t = p1_t.plot(pen=pg.mkPen('g'))
    curve3_t.setData(t_ax, fRx3_r)
    label3_t = pg.TextItem("P5.1 Rx0 in GREEN")
    label3_t.setParentItem(p1_t)
    label3_t.setPos(65, 46) # Change Y position for each label
    curve4_t = p1_t.plot(pen=pg.mkPen('y'))
    curve4_t.setData(t_ax, fRx4_r)
    label4_t = pg.TextItem("P5.1 Rx1 in YELLOW")
    label4_t.setParentItem(p1_t)
    label4_t.setPos(65, 68) # Change Y position for each label

    # CORRECTED TIME DATA
    # Change the pen for clarity - 'b' is blue
    curve1_c = p3_t.plot(pen=pg.mkPen('b'))
    curve1_c.setData(t_ax, fRx1_r)
    label1_c = pg.TextItem("P2.1 Rx0 in BLUE")
    label1_c.setParentItem(p3_t)
    label1_c.setPos(65, 2)
    curve2_c = p3_t.plot(pen=pg.mkPen('r'))
    curve2_c.setData(t_ax, DfP3_r)
    label2_c = pg.TextItem("P2.1 Rx1 in RED")
    label2_c.setParentItem(p3_t)
    label2_c.setPos(65, 24) # Change Y position for each label
    curve3_c = p3_t.plot(pen=pg.mkPen('g'))
    curve3_c.setData(t_ax, DfP4_r)
    label3_c = pg.TextItem("P5.1 Rx0 in GREEN")
    label3_c.setParentItem(p3_t)
    label3_c.setPos(65, 46) # Change Y position for each label
    curve4_c = p3_t.plot(pen=pg.mkPen('y'))
    curve4_c.setData(t_ax, DfP5_r)
    label4_c = pg.TextItem("P5.1 Rx1 in YELLOW")
    label4_c.setParentItem(p3_t)
    label4_c.setPos(65, 68) # Change Y position for each label

    # curve5_t = p2_t.plot(pen=pg.mkPen('c'))
    # curve5_t.setData(t_ax, fTX_r)
    # label5_t = pg.TextItem("P4.1 TX Baseband in CYAN")
    # label5_t.setParentItem(p2_t)
    # label5_t.setPos(65, 2) # Change Y position for each label

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
    # p1 = win_raw2.addPlot()
    # p1.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    # p1.setLabel('left', 'Relative Gain', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    # curve1 = p1.plot(pen=pg.mkPen('b'))
    # curve1.setData(xf, fRx1_db)
    # label1 = pg.TextItem("P2.1 Rx0 in BLUE")
    # label1.setParentItem(p1)
    # label1.setPos(65, 2)
    # curve2 = p1.plot(pen=pg.mkPen('r'))
    # curve2.setData(xf, fRx2_db)
    # label2 = pg.TextItem("P2.1 Rx1 in RED")
    # label2.setParentItem(p1)
    # label2.setPos(65, 24) # Change Y position for each label
    # curve3 = p1.plot(pen=pg.mkPen('g'))
    # curve3.setData(xf, fRx3_db)
    # label3 = pg.TextItem("P5.1 Rx0 in GREEN")
    # label3.setParentItem(p1)
    # label3.setPos(65, 46) # Change Y position for each label
    # curve4 = p1.plot(pen=pg.mkPen('y'))
    # curve4.setData(xf, fRx4_db)
    # label4 = pg.TextItem("P5.1 Rx1 in YELLOW")
    # label4.setParentItem(p1)
    # label4.setPos(65, 68) # Change Y position for each label
    
    # Visualize data: Window 2 (Raster)
    # p2 = win_raw3.addPlot()
    # p2.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    # p2.setLabel('left', 'Relative Gain - P2.1 Rx0', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    # p3 = win_raw3.addPlot()
    # p3.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    # p3.setLabel('left', 'Relative Gain - P2.1 Rx1', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    # p4 = win_raw3.addPlot()
    # p4.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    # p4.setLabel('left', 'Relative Gain - P5.1 Rx0', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    # p5 = win_raw3.addPlot()
    # p5.setLabel('bottom', 'Frequency', 'MHz', **{'color': '#FFF', 'size': '14pt'})
    # p5.setLabel('left', 'Relative Gain - P5.1 Rx1', 'dBfs', **{'color': '#FFF', 'size': '14pt'})
    
    # Change the pen to any other color for clarity - 'b' is blue
    # curve1a = p2.plot(pen=pg.mkPen('b'))
    # curve1a.setData(xf, fRx1_db)
    # label1a = pg.TextItem("P2.1 Rx0 in BLUE")
    # label1a.setParentItem(p2)
    # label1a.setPos(65, 2)
    # curve2a = p3.plot(pen=pg.mkPen('r'))
    # curve2a.setData(xf, fRx2_db)
    # label2a = pg.TextItem("P2.1 Rx1 in RED")
    # label2a.setParentItem(p3)
    # label2a.setPos(65, 2) # Change Y position for each label
    # curve3a = p4.plot(pen=pg.mkPen('g'))
    # curve3a.setData(xf, fRx3_db)
    # label3a = pg.TextItem("P5.1 Rx0 in GREEN")
    # label3a.setParentItem(p4)
    # label3a.setPos(65, 2) # Change Y position for each label
    # curve4a = p5.plot(pen=pg.mkPen('y'))
    # curve4a.setData(xf, fRx4_db)
    # label4a = pg.TextItem("P5.1 Rx1 in YELLOW")
    # label4a.setParentItem(p5)
    # label4a.setPos(65, 2) # Change Y position for each label
    
else: 
    raise ValueError(print("Not a valid domain/graph type."))

# Keep QT Graph open until exiting
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec()