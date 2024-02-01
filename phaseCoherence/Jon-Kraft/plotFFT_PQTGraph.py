"""
Jon Kraft, Oct 30 2022
https://github.com/jonkraft/Pluto_Beamformer
video walkthrough of this at:  https://www.youtube.com/@jonkraft

"""
# Copyright (C) 2020 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.

import sys
print(f'sys.path = {sys.path}')       # Edit JB: may need to add path to PYTHONPATH for OSError: [Errno 16] Device or resource busy

import adi
import matplotlib.pyplot as plt
import pyqtgraph as pg  
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np
import time
import math

'''Setup'''
samp_rate = 2e6             # must be <= 30.72 MHz if both channels are enabled
NumSamples = 2**12
rx_lo = 2.3e9
rx_mode = "manual"          # can be "manual" or "slow_attack"
rx_gain0 = 40
rx_gain1 = 40
tx_lo = rx_lo
tx_gain = -3
fc0 = int(200e3)

''' Set distance between Rx antennas '''
d_wavelength = 0.5                      # distance between elements as a fraction of wavelength.  This is normally 0.5
wavelength = 3E8 / rx_lo                # wavelength of the RF carrier
d = d_wavelength * wavelength           # distance between elements in meters
print("Set distance between Rx Antennas to ", int(d*1000), "mm")

'''Create Radio'''
sdr = adi.ad9361(uri='ip:192.168.2.1')

'''Configure properties for the Radio'''
sdr.rx_enabled_channels = [0, 1]
sdr.sample_rate = int(samp_rate)
sdr.rx_rf_bandwidth = int(fc0*3)
sdr.rx_lo = int(rx_lo)
sdr.gain_control_mode = rx_mode
sdr.rx_hardwaregain_chan0 = int(rx_gain0)
sdr.rx_hardwaregain_chan1 = int(rx_gain1)
sdr.rx_buffer_size = int(NumSamples)
sdr._rxadc.set_kernel_buffers_count(1)      # set buffers to 1 (instead of the default 4) to avoid stale data on Pluto
sdr.tx_rf_bandwidth = int(fc0*3)
sdr.tx_lo = int(tx_lo)
sdr.tx_cyclic_buffer = True
sdr.tx_hardwaregain_chan0 = int(tx_gain)
sdr.tx_hardwaregain_chan1 = int(-88)
sdr.tx_buffer_size = int(2**18)

'''Program Tx and Send Data'''
fs = int(sdr.sample_rate)
N = 2**16
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i0 = np.cos(2 * np.pi * t * fc0) * 2 ** 14
q0 = np.sin(2 * np.pi * t * fc0) * 2 ** 14
iq0 = i0 + 1j * q0
sdr.tx([iq0,iq0])                           # Send Tx data.

xf = np.fft.fftfreq(NumSamples, ts)         # Assign frequency bins
xf = np.fft.fftshift(xf)/1e6

def calcTheta(phase):
    # calculates the steering angle for a given phase delta (phase is in deg)
    # steering angle is theta = arcsin(c*deltaphase/(2*pi*f*d)
    arcsin_arg = np.deg2rad(phase) * 3E8 / (2 * np.pi * rx_lo * d)
    arcsin_arg = max(min(1, arcsin_arg), -1)     # arcsin argument must be between 1 and -1, or numpy will throw a warning
    calc_theta = np.rad2deg(np.arcsin(arcsin_arg))
    return calc_theta

def dbfs(raw_data):                         # function to convert IQ samples to FFT plot, scaled in dBFS
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20*np.log10(np.abs(s_shift)/(2**11))   # Pluto is a signed 12 bit ADC, so use 2^11 to convert to dBFS
    return s_dbfs

'''Collect Data'''
for i in range(20):                         # let Pluto run for a bit, to do all its calibrations, then get a buffer
    data = sdr.rx()

''' Set up FFT Window '''
win = pg.GraphicsLayoutWidget(show=True, size=(1200, 600))
p1 = win.addPlot()
p1.setXRange(-1.00, 1.00)
p1.setYRange(-100, 0)
p1.setLabel('bottom', 'frequency', '[MHz]', **{'color': '#FFF', 'size': '14pt'})
p1.setLabel('left', 'Rx0 + Rx1', '[dBfs]', **{'color': '#FFF', 'size': '14pt'})
# Labels
phaseLabel = pg.TextItem("Phase shift = 0 deg")
phaseLabel.setParentItem(p1)
phaseLabel.setPos(65, 2)
peakPhaseLabel = pg.TextItem("Peak delay = N/A")
peakPhaseLabel.setParentItem(p1)
peakPhaseLabel.setPos(65, 22)
steerLabel = pg.TextItem("Steer Angle = 0 deg")
steerLabel.setParentItem(p1)
steerLabel.setPos(65, 42)
peakSteerLabel = pg.TextItem("Estimated DOA = N/A")
peakSteerLabel.setParentItem(p1)
peakSteerLabel.setPos(65, 62)
# Curves
baseCurve = p1.plot()
baseCurve.setZValue(10)
peakCurve = p1.plot(pen=pg.mkPen('b'))

''' Set up RADAR window '''
def addText(plot, degree, x, y):
    text = pg.TextItem(degree)
    plot.addItem(text)
    text.setPos(x, y)
p2 = win.addPlot()
p2.setAspectLocked()
p2.setMouseEnabled(x=False, y=False)
# Add polar grid lines
p2.addLine(x=0, pen=0.2)
p2.addLine(y=0, pen=0.2)
for r in range(2, 22, 2):
    circle = QtWidgets.QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
    circle.setPen(pg.mkPen(0.2))
    p2.addItem(circle)
    p2.hideAxis('bottom')
    p2.hideAxis('left')
# Add text
addText(p2, "0°", -1, 22)
addText(p2, "45°", 14, 16)
addText(p2, "90°", 20, 1)
addText(p2, "135°", 14, -14)
addText(p2, "180°", -1, -20)
addText(p2, "225°", -17, -14)
addText(p2, "270°", -23, 1)
addText(p2, "315°", -17, 16)
# Arrows
steerArrow = pg.ArrowItem()
steerArrow.setStyle(angle=-90, tipAngle=8, tailLen=200, brush=pg.mkColor('w'))
p2.addItem(steerArrow)
peakSteerArrow = pg.ArrowItem()
peakSteerArrow.setStyle(angle=-90, tipAngle=8, tailLen=200, brush=pg.mkColor('b'))
p2.addItem(peakSteerArrow)

''' Rx Data '''
data = sdr.rx()
Rx_0 = data[0]
Rx_1 = data[1]

'''Initialize loop variables'''
peak_sum = -10000
peak_delay = -10000
peak_steer_angle = -10000
delay_phases = np.arange(-180, 182, 2)  # phase delay in degrees
i = 0 # index for iterating through phases
phaseIncrement = 1 # dictates phase incrementation in loop - integers
rpm = 0.01 # speed of loop in seconds
phase_cal = -58 # start with 0 to calibrate
rotateMode = "loop" # 'loop' or 'bounce'
peakToggle = True # Bool for keeping track of peak values

def rescan():
    global Rx_0, Rx_1, peak_sum, peak_delay, peak_steer_angle
    data = sdr.rx()
    Rx_0 = data[0]
    Rx_1 = data[1]
    peak_sum = -10000
    peak_delay = -10000
    peak_steer_angle = -10000

def rotate():
    global phaseLabel, peakPhaseLabel, steerLabel, peakSteerLabel, baseCurve, peakCurve, peak_steer_angle, steer_angle, steerArrow, peakSteerArrow, peak_sum, peak_delay, i, phaseIncrement, rpm, phase_cal, rotateMode, peakToggle

    phase_delay = delay_phases[i]
    delayed_Rx_1 = Rx_1 * np.exp(1j*np.deg2rad(phase_delay+phase_cal))
    delayed_sum = dbfs(Rx_0 + delayed_Rx_1)
    # Find max delay and max steering angle
    if (peakToggle and np.max(delayed_sum) > np.max(peak_sum)):
        peak_sum = delayed_sum 
        peak_delay = phase_delay
        peak_steer_angle = int(calcTheta(peak_delay))

    ''' FFT Plot '''
    if (peakToggle):
        peakCurve.setData(xf, peak_sum)
    baseCurve.setData(xf, delayed_sum)
    steer_angle = int(calcTheta(phase_delay))
    # Set labels
    phaseLabel.setText("Phase shift = {} deg".format(phase_delay))
    steerLabel.setText("Steering Angle = {} deg".format(steer_angle))
    if (peakToggle):
        peakPhaseLabel.setText("Peak delay = {} deg".format(peak_delay))
        peakSteerLabel.setText("Estimated DOA = {} deg".format(peak_steer_angle))

    ''' RADAR Plot '''
    p2.removeItem(peakSteerArrow)
    if (peakToggle):
        peakSteerArrow = pg.ArrowItem()
        peakSteerArrow.setStyle(angle=peak_steer_angle-90, tipAngle=8, tailLen=200, brush=pg.mkColor('b'))
        p2.addItem(peakSteerArrow)
    p2.removeItem(steerArrow)
    steerArrow = pg.ArrowItem()
    steerArrow.setStyle(angle=steer_angle-90, tipAngle=8, tailLen=200, brush=pg.mkColor('w'))
    p2.addItem(steerArrow)

    # Increment through phases - Reset peaks
    i=i+math.floor(phaseIncrement)
    if (rotateMode == 'loop'):
        if (i>=len(delay_phases)):
            i=0
            rescan()
        elif (i<=-1):
            i=len(delay_phases)-1
            rescan()
    elif (rotateMode == 'bounce'):
        if (i>=len(delay_phases) or i<=-1):
            phaseIncrement=-1*phaseIncrement
            i=i+math.floor(phaseIncrement)
            rescan()

    # Control rate of rotation
    time.sleep(rpm)
    
timer = pg.QtCore.QTimer()
timer.timeout.connect(rotate)
timer.start(0)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        # QtGui.QApplication.instance().exec_() # 2023-12-01 JB: does not work (see next line)
        QtGui.QGuiApplication.instance().exec()

sdr.tx_destroy_buffer()