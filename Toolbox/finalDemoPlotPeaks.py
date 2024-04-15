'''
Joel Brigida & Peyton Adkins
Modified Plot Peaks Code for Testing multiple PlutoSDR units simultaneously.
All modifications are ours: Copyright 2023 Joel Brigida & Peyton Adkins
--------------------------------------------------------------------------
JB: Valid USA ISM Bands: https://en.wikipedia.org/wiki/ISM_radio_band
Note that ISM bands in the USA do not require a license to operate on.
The original PlotPeaks used 2.3 GHz which is outside of the ISM band.
These ISM bands should work with a TX modified PlutoSDR, please use RESPONSIBLY.
40.66 MHz - 40.7 MHz
433.05 MHz - 434.79 MHz
902 MHz - 928 MHz
2.4 GHz - 2.5 GHz
5.725 GHz - 5.875 GHz
---------------------------------------------------------------------------
Note 1) on Pluto TX Gain Settings: https://wiki.gnuradio.org/index.php/PlutoSDR_Sink
Attenuation TX1 (dB):
Controls attenuation for TX1. The range is from 0 to 89.75 dB in 0.25dB steps. Note: Maximum output occurs at 0 attenuation.
** In python, this must be a negative number, but in GNU Radio the number is positive.
-----------------------------------------------------------------------------------
Note 2) Pluto RX Gain Settings: https://wiki.gnuradio.org/index.php/PlutoSDR_Source
RF Bandwidth:
Configures RX analog filters: RX TIA LPF and RX BB LPF. limits: >= 200000 and <= 52000000
Manual Gain (Rx1)(dB):
gain value, max of 71 dB, or 62 dB when over 4 GHz center freq
'''
## For any reused code:
# Jon Kraft, Oct 30 2022
# https://github.com/jonkraft/Pluto_Beamformer
# video walkthrough of this at:  https://www.youtube.com/@jonkraft
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
#       on or directly connected to an Analog Devices Inc. component

from sys import path
#print(f'sys.path = {path}')        # Edit JB: may need to add path to PYTHONPATH for OSError: [Errno 16] Device or resource busy
from adi import ad9361
from datetime import datetime
import pyqtgraph as pg  
from pyqtgraph.Qt import QtCore, QtGui#, QtWidgets
import numpy as np
import pylab as pl
import math
import time

''' Function To Trim ndarray data '''
def trimDelay(input, delayDelta):
    input = np.pad(input, (0, delayDelta), 'constant', constant_values=(0))
    input = input[delayDelta:]
    return input

''' Function for padding ndarray data '''
def padDelay(input, delayDelta):
    length = len(input)
    input = np.pad(input, (delayDelta, 0), 'constant', constant_values=(0))
    input = input[:length]
    return input

''' Generate BPSK (Binary Phase Shift Keying) - Emerson '''
def generate_bpsk(data, samp_rate, bit_len):
    num_bits = data.shape[0]
    samples_per_bit = math.floor(samp_rate*bit_len)
    #
    iq = np.empty(0)
    for idx in range(num_bits):
        iq = np.append(iq, data[idx] * np.ones([int(samples_per_bit)]))
    #
    # Add complex component
    iq = iq + 1j * np.zeros(iq.shape[0])
    #
    return iq

''' Function for cross-correlation - Krysik '''
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
        
    pre = pl.fft(pl.pad(X, (maxlag,postpad_X), 'constant', constant_values=(0, 0)))
    post = pl.fft(pl.pad(Y, (0,postpad_Y), 'constant', constant_values=(0, 0)))
    cor = pl.ifft(pre * pl.conj(post))
    R = cor[0:2 * maxlag]
    return R

''' Function for computing and finding delays - Krysik '''
def compute_phase_offset_and_delay(ref_data, Rx_data):

    result_corr = xcorrelate(ref_data, Rx_data, int(len(ref_data) / 2))
    max_position = np.argmax(abs(result_corr))
    delay = len(result_corr) / 2 - max_position

    phase_diff = result_corr[max_position] / np.sqrt(np.mean(np.real(Rx_data)**2 + np.imag(Rx_data)**2))
    phase_diff = np.angle(phase_diff)/ np.pi * 180

    return int(phase_diff), int(delay)

''' Calculate Steering Angle using Phase Difference - Kraft '''
def calcTheta(phase):
    # calculates the steering angle for a given phase delta (phase is in deg)
    # steering angle is theta = arcsin(c * deltaphase / (2 * pi * f * d)
    arcsin_arg = np.deg2rad(phase) * 3e8 / (2 * np.pi * rx_lo * d)
    arcsin_arg = max(min(1, arcsin_arg), -1) # arcsin argument must be between 1 and -1, or numpy will throw a warning
    calc_theta = np.rad2deg(np.arcsin(arcsin_arg))
    return calc_theta

''' Convert IQ samples to FFT Plot Display scaled in dBfs - Kraft '''
def dbfs(raw_data):
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20 * np.log10(np.abs(s_shift) / (2**11))     # Pluto is a signed 12 bit ADC, so use 2^11 to convert to dBFS
    return s_dbfs


''' Basic RF Setup '''
# must be <=30.72 MHz if both channels are enabled
samp_rate = 1e6                     # 1 MHz: 1 Mil Samples / Sec (1 sample per microsecond)
NumSamples = 2**12
rx_lo = 915e6                       # 915 MHz (Keep it inside the USA ISM band: 902 - 928 MHz)
rx_mode = "manual"                  # can be "manual" or "slow_attack"
#rx0_gain_sdr1 = 20                  # Each RX Channel now has its own gain setting (Tested with GNURadio)
#rx1_gain_sdr1 = 20
rx0_gain_sdr2 = 20
rx1_gain_sdr2 = 20
rx0_gain_sdr3 = 20
rx1_gain_sdr3 = 20
rx0_gain_sdr4 = 20
rx1_gain_sdr4 = 20
tx_lo = rx_lo
tx_gain = -3                        # Same as positive value in GNU Radio Sink
fc0 = int(200e3)                    # 200 kHz

''' Set distance between Rx antennas '''
d_wavelength = 0.5                  # wavelength between elements.
wavelength = 3e8 / rx_lo            # Frequency of the RF Carrier in Hz
d = d_wavelength * wavelength       # distance between elements in meters
print("Set distance between Rx Antennas to ", int(d*1000), "mm")


''' Create Radios '''
sdr0 = ad9361(uri='ip:192.168.6.1') # Pluto #1 (Transmitter)
sdr1 = ad9361(uri='ip:192.168.2.1') # Pluto #2
sdr2 = ad9361(uri='ip:192.168.5.1') # Pluto #5
sdr3 = ad9361(uri='ip:192.168.3.1') # Pluto #3
sdr4 = ad9361(uri='ip:192.168.4.1') # Pluto #4

''' Configure All PlutoSDR Radio Channels '''
#sdr1.rx_enabled_channels = [0, 1]
sdr1.rx_enabled_channels = [0, 1]
sdr2.rx_enabled_channels = [0, 1]
sdr3.rx_enabled_channels = [0, 1]
#sdr1.sample_rate = int(samp_rate)
sdr1.sample_rate = int(samp_rate)
sdr2.sample_rate = int(samp_rate)
sdr3.sample_rate = int(samp_rate)
#sdr1.rx_rf_bandwidth = int(fc0 * 3)
sdr1.rx_rf_bandwidth = int(fc0 * 3)
sdr2.rx_rf_bandwidth = int(fc0 * 3)
sdr3.rx_rf_bandwidth = int(fc0 * 3)
#sdr1.rx_lo = int(rx_lo)
sdr1.rx_lo = int(rx_lo)
sdr2.rx_lo = int(rx_lo)
sdr3.rx_lo = int(rx_lo)
#sdr1.gain_control_mode = rx_mode
sdr1.gain_control_mode = rx_mode
sdr2.gain_control_mode = rx_mode
sdr3.gain_control_mode = rx_mode
#sdr1.rx_hardwaregain_chan0 = int(rx0_gain_sdr1)
sdr1.rx_hardwaregain_chan0 = int(rx0_gain_sdr2)
sdr2.rx_hardwaregain_chan0 = int(rx0_gain_sdr3)
sdr3.rx_hardwaregain_chan0 = int(rx0_gain_sdr4)
#sdr1.rx_hardwaregain_chan1 = int(rx1_gain_sdr1)
sdr1.rx_hardwaregain_chan1 = int(rx1_gain_sdr2)
sdr2.rx_hardwaregain_chan1 = int(rx1_gain_sdr3)
sdr3.rx_hardwaregain_chan1 = int(rx1_gain_sdr4)
#sdr1.rx_buffer_size = int(NumSamples)
sdr1.rx_buffer_size = int(NumSamples)
sdr2.rx_buffer_size = int(NumSamples)
sdr3.rx_buffer_size = int(NumSamples)
#sdr1._rxadc.set_kernel_buffers_count(1)        # set buffers to 1 (instead of the default 4) to avoid stale data on Pluto
sdr1._rxadc.set_kernel_buffers_count(1)
sdr2._rxadc.set_kernel_buffers_count(1)
sdr3._rxadc.set_kernel_buffers_count(1)
sdr0.tx_rf_bandwidth = int(fc0 * 3)             # ONLY TX 1 of PlutoSDR 1 will have TX capability.
sdr0.tx_lo = int(tx_lo)
sdr0.tx_cyclic_buffer = True
sdr0.tx_hardwaregain_chan0 = int(tx_gain)       # ONLY TX1 of PlutoSDR 1 is the transmitter.
#sdr2.tx_hardwaregain_chan0 = int(-88)          # Shut Off all other TX Channels for all Plutos
# sdr3.tx_hardwaregain_chan0 = int(-88)
# sdr4.tx_hardwaregain_chan0 = int(-88)
sdr0.tx_hardwaregain_chan1 = int(-88)
#sdr2.tx_hardwaregain_chan1 = int(-88)
# sdr3.tx_hardwaregain_chan1 = int(-88)
# sdr4.tx_hardwaregain_chan1 = int(-88)
sdr0.tx_buffer_size = int(2**18)                # TX Buffer size: 2^18 = 262144

''' TX Mode Selection for TX Pluto: '''
MODE = "carrier" # "bpsk" or "carrier"

if MODE == "bpsk": # Beta testing

    ''' Program SDR1 TX1 and Send Data From PlutoSDR 1 to all other RX Nodes '''
    # Barker Sequence
    b13 = np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1])

    # Carrier Signal
    fs = int(sdr0.sample_rate)
    N = 2**16
    ts = 1 / float(fs)
    t = np.arange(0, N * ts, ts)
    i0 = np.cos(2 * np.pi * t * fc0) * 2**14
    q0 = np.sin(2 * np.pi * t * fc0) * 2**14
    iq0 = i0 + 1j * q0

    # BPSK
    bpsk = generate_bpsk(iq0, 50, 13)
    sdr0.tx([iq0, iq0])  # Send Tx data.

elif MODE == "carrier": # Default Mode

    fs = int(sdr0.sample_rate)
    N = 2**16
    ts = 1 / float(fs)
    t = np.arange(0, N * ts, ts)
    i0 = np.cos(2 * np.pi * t * fc0) * 2**14
    q0 = np.sin(2 * np.pi * t * fc0) * 2**14
    iq0 = i0 + 1j * q0
    sdr0.tx([iq0, iq0])  # Send Tx data.

else:
    print("Not a valid TX Mode....Exiting")
    exit(-1)


xf = np.fft.fftfreq(NumSamples, ts) # Assign frequency bins and "zoom in" to the fc0 signal on those frequency bins
xf = np.fft.fftshift(xf) / 1e6
signal_start = int(NumSamples * (samp_rate / 2 + fc0 / 2) / samp_rate)
signal_end = int(NumSamples * (samp_rate / 2 + fc0 * 2) / samp_rate)

''' Set up FFT Window '''
win = pg.GraphicsLayoutWidget(show=True, size=(1200, 600))
p1 = win.addPlot()
# p1.setXRange(-1.00, 1.00)
p1.setYRange(-100, 10)
p1.setLabel('bottom', 'frequency', '[MHz]', **{'color': '#FFF', 'size': '14pt'})
p1.setLabel('left', 'P1Rx + P2Rx', '[dBfs]', **{'color': '#FFF', 'size': '14pt'})
# Labels
peakSignalLabel = pg.TextItem("Peak Signal at 0 deg")
peakSignalLabel.setParentItem(p1)
peakSignalLabel.setPos(65, 2)
phaseLabelP2Rx0 = pg.TextItem("Phase shift P2Rx0 = 0 deg")
phaseLabelP2Rx0.setParentItem(p1)
phaseLabelP2Rx0.setPos(65, 22)
phaseLabelP3Rx0 = pg.TextItem("Phase shift P3Rx0 = 0 deg")
phaseLabelP3Rx0.setParentItem(p1)
phaseLabelP3Rx0.setPos(65, 42)
peakSteerLabel = pg.TextItem("Estimated DOA = N/A")
peakSteerLabel.setParentItem(p1)
peakSteerLabel.setPos(65, 62)
# Line
vertiLine = pg.InfiniteLine(pen=pg.mkPen('r', width=2, style=QtCore.Qt.SolidLine))
p1.addItem(vertiLine)
# Curves
baseCurve = p1.plot()
baseCurve.setZValue(10)

''' Set up Time Sync Window '''
win_raw = pg.GraphicsLayoutWidget(show=True, size=(1200, 600), title="Time Domain Output")
p1_t = win_raw.addPlot()
p1_t.setLabel('bottom', 'Time', 'sec', **{'color': '#FFF', 'size': '14pt'})
p1_t.setLabel('left', 'Amplitude', **{'color': '#FFF', 'size': '14pt'})
p1_t.setYRange(-650, 650, padding=0)
# Time axis
t_ax = np.arange(NumSamples) / samp_rate
# Curves and labels
curve1_t = p1_t.plot(pen=pg.mkPen('b'))
label1_t = pg.TextItem("P1 Rx0 in BLUE")
label1_t.setParentItem(p1_t)
label1_t.setPos(65, 2)
curve2_t = p1_t.plot(pen=pg.mkPen('r'))
label2_t = pg.TextItem("P1 Rx1 in RED")
label2_t.setParentItem(p1_t)
label2_t.setPos(65, 24) # Change Y position for each label
curve3_t = p1_t.plot(pen=pg.mkPen('g'))
label3_t = pg.TextItem("P2 Rx0 in GREEN")
label3_t.setParentItem(p1_t)
label3_t.setPos(65, 46) # Change Y position for each label
curve4_t = p1_t.plot(pen=pg.mkPen('y'))
label4_t = pg.TextItem("P2 Rx1 in YELLOW")
label4_t.setParentItem(p1_t)
label4_t.setPos(65, 68) # Change Y position for each label
curve5_t = p1_t.plot(pen=pg.mkPen('c'))
label5_t = pg.TextItem("P3 Rx1 in CYAN")
label5_t.setParentItem(p1_t)
label5_t.setPos(65, 90) # Change Y position for each label
curve6_t = p1_t.plot(pen=pg.mkPen('m'))
label6_t = pg.TextItem("P3 Rx1 in MAGENTA")
label6_t.setParentItem(p1_t)
label6_t.setPos(65, 102) # Change Y position for each label


''' Collect Data '''
# let each Pluto run for a bit, to do all its calibrations, then get a buffer
for i in range(20):
    data1 = sdr1.rx()
    data2 = sdr2.rx()
    data3 = sdr3.rx()

''' Main Loop '''
def rotate():
    # Speed modifier for sweep
    rpm = 0.1
    # Receieve Rx data
    data1 = sdr1.rx()
    data2 = sdr2.rx()
    data3 = sdr3.rx()
    #
    Rx_0a = data1[0]          # PlutoSDR 1, RX 0
    Rx_0b = data2[0]          # PlutoSDR 2, RX 0
    Rx_0c = data3[0]          # PlutoSDR 3, RX 0
    peak_sum = []
    
    # Find trigger delays and phase offsets
    phase_cal_0b, delay_0b = compute_phase_offset_and_delay(Rx_0a, Rx_0b)
    phase_cal_0c, delay_0c = compute_phase_offset_and_delay(Rx_0a, Rx_0c)
    
    # Create an Array for -180 - 180 degrees sweep
    delay_phases = np.arange(-160, 160, 2)    
    # delay_phases = np.array([-120, 0, 120]) 
    
    # Set delays   
    if delay_0b < 0:
        Rx_0b = padDelay(Rx_0b, int(-delay_0b))
    elif delay_0b > 0:
        Rx_0b = trimDelay(Rx_0b, int(delay_0b))
    if delay_0c < 0:
        Rx_0c = padDelay(Rx_0c, int(-delay_0c))
    elif delay_0c > 0:
        Rx_0c = trimDelay(Rx_0c, int(delay_0c))

    ''' Phase shift by each degree from -180 to 180 and store peak signal '''
    for phase_delay in delay_phases:   
        peak_sum_avg = []
        # Compute phase shift
        delayed_Rx_0b = Rx_0b * np.exp(1j * np.deg2rad(2 * phase_delay + phase_cal_0b)) # PlutoSDR 2 RX 0
        delayed_Rx_0c = Rx_0c * np.exp(1j * np.deg2rad(4 * phase_delay + phase_cal_0c)) # PlutoSDR 3 RX 0
        # Sum shifted & delayed Rx data 
        delayed_sum = dbfs( Rx_0a + delayed_Rx_0b  + delayed_Rx_0c )
        peak_sum_avg.append(delayed_sum[signal_start:signal_end])
        
        ''' Sync Time Plot '''
        curve1_t.setData(t_ax, np.real(Rx_0a))
        curve3_t.setData(t_ax, np.real(Rx_0b))
        curve5_t.setData(t_ax, np.real(Rx_0c))
        peak_sum_value = sum(peak_sum_avg) / len(peak_sum_avg)
        peak_sum.append(np.max(peak_sum_value)) # np.max(delayed_sum[signal_start:signal_end])
    
    # Peak delay and steering angle
    peak_dbfs = np.max(peak_sum)
    peak_delay_index = np.where(peak_sum == peak_dbfs)
    peak_delay = delay_phases[peak_delay_index[0][0]]
    steer_angle = int(calcTheta(peak_delay))

    ''' Peak Sum Plot '''
    baseCurve.setData(delay_phases, peak_sum)
    p1.removeItem(vertiLine)
    vertiLine.setPos(peak_delay)
    p1.addItem(vertiLine)
    # Set labels
    peakSignalLabel.setText(f'Peak Signal at {round(peak_delay, 1)} deg phase delay')
    phaseLabelP2Rx0.setText(f'Phase offset P2Rx0 = {phase_cal_0b} deg')
    phaseLabelP3Rx0.setText(f'Phase offset P3Rx0 = {phase_cal_0c} deg')
    peakSteerLabel.setText(f'If d = {int(d*1000)}mm, then steering angle = {steer_angle} deg')

    # Control rate of rotation
    time.sleep(rpm)
    
timer = pg.QtCore.QTimer()
timer.timeout.connect(rotate)
timer.start(0)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec()

sdr0.tx_destroy_buffer()