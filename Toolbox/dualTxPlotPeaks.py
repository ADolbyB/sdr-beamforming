'''
Joel Brigida & Peyton Adkins
Modified Plot Peaks Code for Testing multiple PlutoSDR units simultaneously.
This specific modification aims to account for CPU delays between multiple SDRs
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
Attenuation TX0 and TX1 (dB):
Controls attenuation for TX0 and TX1. The range is from 0 to 89.75 dB in 0.25dB steps. Note: Maximum output occurs at 0 attenuation.
** In python, this must be a negative number, but in GNU Radio the number is positive.
-----------------------------------------------------------------------------------
Note 2) Pluto RX Gain Settings: https://wiki.gnuradio.org/index.php/PlutoSDR_Source
RF Bandwidth:
Configures RX analog filters: RX TIA LPF and RX BB LPF. limits: >= 200000 and <= 52000000
Manual Gain (Rx1)(dB):
gain value, max of 71 dB, or 62 dB when over 4 GHz center freq
-----------------------------------------------------------------------------------
Note 3) The physical setup for this script assumes a designated Pluto (Pluto 1) to have one TX node directly wired to the first Rx nodes (Rx0) of each receiving Pluto (Pluto 2+) split evenly. The other TX node will be used as the transmitter for the desired signal with the remaining Rx nodes (Rx1) of the receiving Plutos (Pluto 2+) arranged within a uniform linear array of equal spacing `d`
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

''' Generate BPSK (Binary Phase Shift Keying) '''
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

# TODO: Compute this function initially with the reference RX data (P1Rx0) and the raw RX data, 
    # then calculate returned values `phase_diff` & `delay` with another call to this function 
    # Using the reference data (again) & the raw data after a TRIM or PAD based off the first computed delay value
''' Function for computing and finding phase offsets '''
def find_phase_offset(ref_data, Rx_data):

    result_corr = xcorrelate(ref_data, Rx_data,int(len(ref_data) / 2))
    max_position = np.argmax(abs(result_corr))

    phase_diff = result_corr[max_position] / pl.sqrt(pl.mean(pl.real(Rx_data)**2 + pl.imag(Rx_data)**2))
    phase_diff = pl.angle(phase_diff)/ pl.pi * 180

    return int(phase_diff)

''' Function for computing and finding trigger delays '''
def find_trigger_delay(ref_data, Rx_data):

    result_corr = xcorrelate(ref_data, Rx_data,int(len(ref_data) / 2))
    max_position = np.argmax(abs(result_corr))
    delay = len(result_corr) / 2 - max_position

    return int(delay)

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

''' Function for correcting trigger delays '''
def correct_trigger_delay(Rx_data, delay):
    if delay < 0:
        return padDelay(Rx_data, int(-delay))
    elif delay > 0:
        return trimDelay(Rx_data, int(delay))
    else:
        return Rx_data

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
#Plot_Compass = False


''' Set distance between Rx antennas '''
d_wavelength = 0.5                  # wavelength between elements.
wavelength = 3e8 / rx_lo            # Frequency of the RF Carrier in Hz
d = d_wavelength * wavelength       # distance between elements in meters
print("Set distance between Rx Antennas to ", int(d*1000), "mm")


''' Create Radios '''
sdr0 = ad9361(uri='ip:192.168.4.1') # Pluto #4 (Transmitter)
sdr1 = ad9361(uri='ip:192.168.2.1') # Pluto #2
sdr2 = ad9361(uri='ip:192.168.5.1') # Pluto #5
sdr3 = ad9361(uri='ip:192.168.3.1') # Pluto #3

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
sdr0.tx_rf_bandwidth = int(fc0 * 3)             # ONLY TX NODES of PlutoSDR 1 will have TX capability.
sdr0.tx_lo = int(tx_lo)
sdr0.tx_cyclic_buffer = True
sdr0.tx_hardwaregain_chan0 = int(tx_gain)       # ONLY TX NODES of PlutoSDR 1 are the transmitters.
#sdr2.tx_hardwaregain_chan0 = int(-88)          # Shut Off all other TX Channels for all Plutos
# sdr3.tx_hardwaregain_chan0 = int(-88)
# sdr4.tx_hardwaregain_chan0 = int(-88)
sdr0.tx_hardwaregain_chan1 = int(tx_gain)
#sdr2.tx_hardwaregain_chan1 = int(-88)
# sdr3.tx_hardwaregain_chan1 = int(-88)
# sdr4.tx_hardwaregain_chan1 = int(-88)
sdr0.tx_buffer_size = int(2**18)                # TX Buffer size: 2^18 = 262144

''' TX Mode Selection for TX Pluto: '''
MODE = "carrier" # "bpsk" or "carrier"

if MODE == "bpsk": # Beta testing

    ''' Program SDR1 TX0 & TX1 and Send Data From PlutoSDR 1 to all other RX Nodes '''
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
delayLabelP2Rx0 = pg.TextItem("Trig delay P2Rx0 = 0 samples")
delayLabelP2Rx0.setParentItem(p1)
delayLabelP2Rx0.setPos(65, 22)
delayLabelP3Rx0 = pg.TextItem("Trig delay P3Rx0 = 0 samples")
delayLabelP3Rx0.setParentItem(p1)
delayLabelP3Rx0.setPos(65, 22)
phaseLabelP2Rx1 = pg.TextItem("Phase shift P2Rx1 = 0 deg")
phaseLabelP2Rx1.setParentItem(p1)
phaseLabelP2Rx1.setPos(65, 42)
phaseLabelP3Rx1 = pg.TextItem("Phase shift P3Rx1 = 0 deg")
phaseLabelP3Rx1.setParentItem(p1)
phaseLabelP3Rx1.setPos(65, 62)
peakSteerLabel = pg.TextItem("Estimated DOA = N/A")
peakSteerLabel.setParentItem(p1)
peakSteerLabel.setPos(65, 82)
# Line
vertiLine = pg.InfiniteLine(pen=pg.mkPen('r', width=2, style=QtCore.Qt.SolidLine))
p1.addItem(vertiLine)
# Curves
baseCurve = p1.plot()
baseCurve.setZValue(10)

''' Rough Estimate CPU Scheduling Time Offsets in Samples (Beta)'''
mastClock = datetime  # Master Clock for all comparisons
P1Clock = datetime    # Starts when Pluto 1 .rx() call is made from main()
P2Clock = datetime    # Starts when Pluto 2 .rx() call is made from main()
P3Clock = datetime    # Starts when Pluto 3 .rx() call is made from main()
masterClock_T = mastClock.now()
print(f'Current mastClock.microsecond: | {masterClock_T}')

''' Collect Data '''
# let each Pluto run for a bit, to do all its calibrations, then get a buffer
# TODO: Debug Terminal Print statements. Sould print # of samples.
for i in range(20):
    #data1 = sdr1.rx()
    print(f'Calibration # {i}')
    data1, data1_T = sdr1.rx(P1Clock)
    print(f'After sdr2.rx(): data2_T        | {data1_T}')
    print(f'After sdr2.rx(): samples        | {int(data1_T.second * samp_rate)}')
    data2, data2_T = sdr2.rx(P2Clock)
    print(f'After sdr3.rx(): data3_T        | {data2_T}')
    print(f'After sdr3.rx(): samples        | {int(data2_T.second * samp_rate)}')
    data3, data3_T = sdr3.rx(P3Clock)
    print(f'After sdr3.rx(): data3_T        | {data3_T}')
    print(f'After sdr3.rx(): samples        | {int(data3_T.second * samp_rate)}')

# TODO: Try Threading processes to receieve data

''' Averaging the Phase Offsets (PIPE DREAM) '''
while(0): # Turned Off For now
    AVERAGING_PHASE = 15
    #phase_cal_1a = []
    #phase_cal_0b = []
    phase_cal_1a = []
    phase_cal_0b = []
    phase_cal_1b = []
    #phase_cal_0d = []
    #phase_cal_1d = []
    for i in range(AVERAGING_PHASE):
        #data1 = sdr1.rx()
        data1, data1_T = sdr1.rx(P1Clock)
        data2, data2_T = sdr2.rx(P2Clock)
        #data4 = sdr4.rx()
        
        #Rx_0a = data1[0]        # PlutoSDR 1, RX 0
        #Rx_1a = data1[1]        # PlutoSDR 1, RX 1
        Rx_0a = data1[0]        # PlutoSDR 2, RX 0
        Rx_1a = data1[1]        # PlutoSDR 2, RX 1
        Rx_0b = data2[0]        # PlutoSDR 2, RX 0
        Rx_1b = data2[1]        # PlutoSDR 2, RX 1
        #Rx_0d = data4[0]        # PlutoSDR 2, RX 0
        #Rx_1d = data4[1]        # PlutoSDR 2, RX 1
        #phase_cal_1a.append(compute_phase_offset(Rx_0a, Rx_1a))
        #phase_cal_0b.append(compute_phase_offset(Rx_0b, Rx_1b))
        phase_1b, delay_1a = find_phase_offset(Rx_0a, Rx_1a)
        phase_0c, delay_0b = find_phase_offset(Rx_0a, Rx_0b)
        phase_1c, delay_1b = find_phase_offset(Rx_0a, Rx_1b)
        phase_cal_1a.append(phase_1b)
        phase_cal_0b.append(phase_0c)
        phase_cal_1b.append(phase_1c)

    #phase_cal_1a = int(sum(phase_cal_1a) / len(phase_cal_1a))
    #phase_cal_0b = int(sum(phase_cal_0b) / len(phase_cal_0b))
    phase_cal_1a = int(sum(phase_cal_1a) / len(phase_cal_1a))
    print("Rx 1 Offset: ", phase_cal_1a)
    print("Rx 1 Delay: ", delay_1a)
    phase_cal_0b = int(sum(phase_cal_0b) / len(phase_cal_0b))
    print("Rx 2 Offset: ", phase_cal_0b)
    print("Rx 2 Delay: ", delay_0b)
    phase_cal_1b = int(sum(phase_cal_1b) / len(phase_cal_1b))
    print("Rx 3 Offset: ", phase_cal_1b)
    print("Rx 3 Delay: ", delay_1b)
    #phase_cal_0d = int(sum(phase_cal_1b) / len(phase_cal_1b))
    #phase_cal_1d = int(sum(phase_cal_1b) / len(phase_cal_1b))

''' Main Loop '''
AVERAGING_SCANS = 1
def sweep():
    # Speed of main loop sweep
    rpm = 0.1
    ## #  # Receieve data #  # ##
    data1, data1_T = sdr1.rx(P1Clock)
    data2, data2_T = sdr2.rx(P2Clock)
    data3, data3_T = sdr3.rx(P3Clock)
    #
    Rx_0a = data1[0]          # PlutoSDR 1, RX 0, the trig delay reference node
    Rx_1a = data1[1]          # PlutoSDR 1, RX 1
    Rx_0b = data2[0]          # PlutoSDR 2, RX 0
    Rx_1b = data2[1]          # PlutoSDR 2, RX 1
    Rx_0c = data3[0]          # PlutoSDR 3, RX 0
    Rx_1c = data3[1]          # PlutoSDR 3, RX 1
    peak_sum = []
    #
    ## #  # Find trigger delays for first Rx nodes #  # ##
    delay_Pluto2 = find_trigger_delay(Rx_0a, Rx_0b) 
    delay_Pluto3 = find_trigger_delay(Rx_0a, Rx_0c)
    #
    # Correct Trigger Delays for second Rx nodes  
    Rx_1b = correct_trigger_delay(Rx_0b, delay_Pluto2) # Uses this trig delay as both Rx0 and Rx1 nodes are from the same Pluto
    Rx_1c = correct_trigger_delay(Rx_1c, delay_Pluto3)
    #
    ## #  # Find phase offsets for second Rx nodes #  # ##
    phase_cal_Pluto2 = find_phase_offset(Rx_1a, Rx_1b)
    phase_cal_Pluto3 = find_phase_offset(Rx_1a, Rx_1c)
    #
    #
    delay_phases = np.arange(-180, 180, 2)    # Create an Array for -180 - 180 degrees sweep
        
    ''' Phase shift by each degree from -180 to 180 and store peak signal '''
    for phase_delay in delay_phases:   
        peak_sum_avg = []
        # Compute phase shift
        delayed_Rx_1b = Rx_1b * np.exp(1j * np.deg2rad(1 * phase_delay + phase_cal_Pluto2)) # PlutoSDR 2 RX 1
        delayed_Rx_1c = Rx_1c * np.exp(1j * np.deg2rad(2 * phase_delay + phase_cal_Pluto3)) # PlutoSDR 3 RX 1
        # Add to peak sum array
        delayed_sum = dbfs( Rx_1a + delayed_Rx_1b + delayed_Rx_1c)
        peak_sum_avg.append(delayed_sum[signal_start:signal_end])
        peak_sum_value = sum(peak_sum_avg) / len(peak_sum_avg)
        peak_sum.append(np.max(peak_sum_value)) # np.max(delayed_sum[signal_start:signal_end])
    
    # Find peak sum
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
    delayLabelP2Rx0.setText(f'Trigger delay P2Rx0 = {delay_Pluto2} samples')
    delayLabelP3Rx0.setText(f'Trigger delay P3Rx0 = {delay_Pluto3} samples')
    phaseLabelP2Rx1.setText(f'Phase shift P2Rx1 = {phase_cal_Pluto2} deg')
    phaseLabelP3Rx1.setText(f'Phase shift P3Rx1 = {phase_cal_Pluto3} deg')
    peakSteerLabel.setText(f'If d = {int(d*1000)}mm, then steering angle = {steer_angle} deg')

    # Control rate of rotation
    time.sleep(rpm)
    
timer = pg.QtCore.QTimer()
timer.timeout.connect(sweep)
timer.start(0)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec()

sdr0.tx_destroy_buffer()