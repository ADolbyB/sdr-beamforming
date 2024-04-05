'''
    Peyton Adkins - Joel Brigida
    This is a Python script that reads data from the specified binary folders of Rx1 and Rx2 data sourced from a single Pluto SDR. This script is derived from the logic of both Jon Kraft's work and Piotr Krysik's work in writing Python code for the Pluto SDR and for synchronizing multiple SDRs in GNU Radio.

    The actual data for the stream output does not indicate any relatice domain. For this script, it is written to be displayed in the time domain to help aid in confirming phase lock across multiple Rx nodes of a single Pluto SDR.
'''

import math
from numpy import *
import numpy as np
from pylab import *
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

'''Function for trimming ndarray data'''
def trimDelay(input, delayDelta):
    input = np.pad(input, (0, delayDelta), 'constant', constant_values=(0))
    input = input[delayDelta:]
    return input

'''Function for padding ndarray data'''
def padDelay(input, delayDelta):
    length = len(input)
    input = np.pad(input, (delayDelta, 0), 'constant', constant_values=(0))
    input = input[:length]
    return input

'''Function for corss-correlation - Krysik'''
def xcorrelate(X,Y,maxlag):
    N = max(len(X), len(Y))
    N_nextpow2 = math.ceil(math.log(N + maxlag,2))
    M = 2**N_nextpow2
    if len(X) < M:
        postpad_X = int(M-len(X)-maxlag)
    else:
        postpad_X = 0

    if len(Y) < M:
        postpad_Y = int(M-len(Y))
    else:
        postpad_Y = 0
        
    pre  = fft( pad(X, (maxlag,postpad_X), 'constant', constant_values=(0, 0)) )
    post = fft( pad(Y, (0,postpad_Y), 'constant', constant_values=(0, 0)) )
    cor  = ifft( pre * conj(post) )
    R = cor[0:2*maxlag]
    return R

'''Function for computing and finding delays - Krysik'''
def compute_and_set_delay(ref_data, Rx_data, Rx_name, samp_rate):

    result_corr = xcorrelate(ref_data, Rx_data,int(len(ref_data)/2))
    max_position = np.argmax(abs(result_corr))
    delay = len(result_corr)/2-max_position

    phase_diff = result_corr[max_position]/sqrt(mean(real(Rx_data)**2+imag(Rx_data)**2))
    # phase_diff = sqrt(var(ref_data)/var(Rx_data))*(exp(1j*angle(phase_diff)))
    phase_diff = angle(phase_diff)/pi*180

    print ("Delay of ", Rx_name, ": ", delay,' | Phase Diff: ', phase_diff, " [deg]")

    # Set phase amplitude correction
    # INSERT
    # phase_amplitude_correction = sqrt(var(ref_data)/var(Rx_data))*(exp(1j*angle(phase_amplitude_correction)))

    # Set delay     
    # if delay < 0:
    #     return trimDelay(Rx_data, int(-delay)) # *samp_rate
    # elif delay > 0:
    #     return padDelay(Rx_data, int(delay)) # *samp_rate
    # else:
    #     return Rx_data

    # return Rx_data * np.exp(1j*np.deg2rad(phase_diff))
    return Rx_data * sqrt(var(ref_data)/var(Rx_data)) * (np.exp(1j*np.deg2rad(phase_diff)))
    

''' File names go here '''
FILE_Rx1 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/LocalPhaseSync/fileOutputRx1"
FILE_Rx2 = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/LocalPhaseSync/fileOutputRx2"

'''Extract data as a complex64'''
# This is the stream output for basic signal processing in GNU Radio
fRx1 = fromfile(open(FILE_Rx1), dtype=np.complex64)
fRx2 = fromfile(open(FILE_Rx2), dtype=np.complex64)
fRx2 = resize(fRx2, fRx1.shape) # resize to match first Rx node
print(fRx1.shape)

DOMAIN = "time" # freq or time
SAMPLE_RATE = 2e6  # should be the same as it was in GNU Radio
NUM_SAMPLES = fRx1.shape[0] # this ensures that it is relative to what is captured

'''Cross-Correlation and Delay Values'''
# DfRx2 = fRx2
DfRx2 = compute_and_set_delay(fRx1, fRx2, "Rx2", SAMPLE_RATE)
nil = compute_and_set_delay(fRx1, DfRx2, "Rx2", SAMPLE_RATE)

'''Create a main QT Window'''
win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="File Output")

'''Visualizing the raw data'''

if DOMAIN == "freq":
    # # # Frequency Domain

    fs = int(SAMPLE_RATE)                       # frequency size
    ts = 1 / float(fs)                          # time size
    xf = np.fft.fftfreq(NUM_SAMPLES, ts)         # Assign frequency bins
    xf = np.fft.fftshift(xf) / 1e6              # Convert to MHz

    # QT does not accept complex data, so we convert IQ samples to FFT
    fRx1_db = dbfs(fRx1)
    fRx2_db = dbfs(DfRx2)

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
    label2.setPos(65, 24) # Change Y position for each label

elif DOMAIN == "time":
    # # # Time Domain

    # QT does not accept complex data, so we separate IQ samples by their real values from their imaginary values
    fRx1_r = real(fRx1)
    fRx2_r_raw = real(fRx2)
    fRx2_r_adj = real(DfRx2)

    # Time axis
    taxs = arange(NUM_SAMPLES)/SAMPLE_RATE
    
    # Visualize raw data
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
    curve2.setData(taxs, fRx2_r_raw)
    label2 = pg.TextItem("Rx2 (raw) in RED")
    label2.setParentItem(p1)
    label2.setPos(65, 24) # Change Y position for each label

    # Visualize synced data
    p2 = win_raw.addPlot()
    p2.setLabel('bottom', 'Time', 'sec', **{'color': '#FFF', 'size': '14pt'})
    p2.setLabel('left', 'Amplitude', **{'color': '#FFF', 'size': '14pt'})
    p2.setYRange(-2, 2, padding=0)
    # p1.setXRange(0, 0.25, padding=0)
    # Change the pen to any other color for clarity - 'b' is blue
    curve3 = p2.plot(pen=pg.mkPen('b'))
    curve3.setData(taxs, fRx1_r)
    label3 = pg.TextItem("Rx1 in BLUE")
    label3.setParentItem(p2)
    label3.setPos(65, 2)
    curve4 = p2.plot(pen=pg.mkPen('r'))
    curve4.setData(taxs, fRx2_r_adj)
    label4 = pg.TextItem("Rx2 (adjusted) in RED")
    label4.setParentItem(p2)
    label4.setPos(65, 24) # Change Y position for each label
    
else: 
    raise ValueError(print("Not a valid domain type."))

# Keep QT Graph open until exiting
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        # QtGui.QApplication.instance().exec_() # 2023-12-01 JB: does not work (see next line)
        QtGui.QGuiApplication.instance().exec()