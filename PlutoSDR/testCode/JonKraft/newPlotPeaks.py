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
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
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

''' Function for computing and finding delays - Krysik '''
def compute_phase_offset(ref_data, Rx_data):

    result_corr = xcorrelate(ref_data, Rx_data,int(len(ref_data) / 2))
    max_position = np.argmax(abs(result_corr))
    delay = len(result_corr) / 2 - max_position

    phase_diff = result_corr[max_position] / pl.sqrt(pl.mean(pl.real(Rx_data)**2 + pl.imag(Rx_data)**2))
    phase_diff = pl.angle(phase_diff)/ pl.pi * 180

    return int(phase_diff)

''' Calculate Steering Angle using Phase Difference '''
def calcTheta(phase):
    # calculates the steering angle for a given phase delta (phase is in deg)
    # steering angle is theta = arcsin(c * deltaphase / (2 * pi * f * d)
    arcsin_arg = np.deg2rad(phase) * 3e8 / (2 * np.pi * rx_lo * d)
    arcsin_arg = max(min(1, arcsin_arg), -1) # arcsin argument must be between 1 and -1, or numpy will throw a warning
    calc_theta = np.rad2deg(np.arcsin(arcsin_arg))
    return calc_theta

''' Convert IQ samples to FFT Plot Display scaled in dBfs '''
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
#rx0_gain_sdr4 = 20
#rx1_gain_sdr4 = 20
tx_lo = rx_lo
tx_gain = -3                        # Same as positive value in GNU Radio Sink
fc0 = int(200e3)                    # 200 kHz
num_scans = 500
Plot_Compass = False


''' Set distance between Rx antennas '''
d_wavelength = 0.5                  # distance between elements as a fraction of wavelength.  This is normally 0.5
wavelength = 3e8 / rx_lo            # wavelength of the RF carrier
d = d_wavelength * wavelength       # distance between elements in meters
print("Set distance between Rx Antennas to ", int(d*1000), "mm")


''' Create Radios '''
sdr1 = ad9361(uri='ip:192.168.4.1') # Pluto #4 (Transmitter)
sdr2 = ad9361(uri='ip:192.168.2.1') # Pluto #3
sdr3 = ad9361(uri='ip:192.168.5.1') # Pluto #4
#sdr4 = ad9361(uri='ip:192.168.5.1') # Pluto #5

''' Configure All PlutoSDR Radio Channels '''
#sdr1.rx_enabled_channels = [0, 1]
sdr2.rx_enabled_channels = [0, 1]
sdr3.rx_enabled_channels = [0, 1]
# sdr4.rx_enabled_channels = [0, 1]
#sdr1.sample_rate = int(samp_rate)
sdr2.sample_rate = int(samp_rate)
sdr3.sample_rate = int(samp_rate)
# sdr4.sample_rate = int(samp_rate)
#sdr1.rx_rf_bandwidth = int(fc0 * 3)
sdr2.rx_rf_bandwidth = int(fc0 * 3)
sdr3.rx_rf_bandwidth = int(fc0 * 3)
# sdr4.rx_rf_bandwidth = int(fc0 * 3)
#sdr1.rx_lo = int(rx_lo)
sdr2.rx_lo = int(rx_lo)
sdr3.rx_lo = int(rx_lo)
# sdr4.rx_lo = int(rx_lo)
#sdr1.gain_control_mode = rx_mode
sdr2.gain_control_mode = rx_mode
sdr3.gain_control_mode = rx_mode
# sdr4.gain_control_mode = rx_mode
#sdr1.rx_hardwaregain_chan0 = int(rx0_gain_sdr1)
sdr2.rx_hardwaregain_chan0 = int(rx0_gain_sdr2)
sdr3.rx_hardwaregain_chan0 = int(rx0_gain_sdr3)
# sdr4.rx_hardwaregain_chan0 = int(rx0_gain_sdr4)
#sdr1.rx_hardwaregain_chan1 = int(rx1_gain_sdr1)
sdr2.rx_hardwaregain_chan1 = int(rx1_gain_sdr2)
sdr3.rx_hardwaregain_chan1 = int(rx1_gain_sdr3)
# sdr4.rx_hardwaregain_chan1 = int(rx1_gain_sdr4)
#sdr1.rx_buffer_size = int(NumSamples)
sdr2.rx_buffer_size = int(NumSamples)
sdr3.rx_buffer_size = int(NumSamples)
# sdr4.rx_buffer_size = int(NumSamples)
#sdr1._rxadc.set_kernel_buffers_count(1)     # set buffers to 1 (instead of the default 4) to avoid stale data on Pluto
sdr2._rxadc.set_kernel_buffers_count(1)
sdr3._rxadc.set_kernel_buffers_count(1)
# sdr4._rxadc.set_kernel_buffers_count(1)
sdr1.tx_rf_bandwidth = int(fc0 * 3)         # ONLY TX 1 of PlutoSDR 1 will have TX capability.
sdr1.tx_lo = int(tx_lo)
sdr1.tx_cyclic_buffer = True
sdr1.tx_hardwaregain_chan0 = int(tx_gain)   # ONLY TX1 of PlutoSDR 1 is the transmitter.
#sdr2.tx_hardwaregain_chan0 = int(-88)       # Shut Off all other TX Channels for all Plutos
# sdr3.tx_hardwaregain_chan0 = int(-88)
# sdr4.tx_hardwaregain_chan0 = int(-88)
sdr1.tx_hardwaregain_chan1 = int(-88)
#sdr2.tx_hardwaregain_chan1 = int(-88)
# sdr3.tx_hardwaregain_chan1 = int(-88)
# sdr4.tx_hardwaregain_chan1 = int(-88)
sdr1.tx_buffer_size = int(2**18)            # TX Buffer size: 2^18 = 262144

''' Mode Selection for TX Pluto: '''
MODE = "carrier" # "bpsk" or "carrier"

if MODE == "bpsk":

    ''' Program SDR1 TX1 and Send Data From PlutoSDR 1 to all other RX Nodes '''
    # Barker Sequence
    b13 = np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1])

    # Carrier Signal
    fs = int(sdr1.sample_rate)
    N = 2**16
    ts = 1 / float(fs)
    t = np.arange(0, N * ts, ts)
    i0 = np.cos(2 * np.pi * t * fc0) * 2**14
    q0 = np.sin(2 * np.pi * t * fc0) * 2**14
    iq0 = i0 + 1j * q0

    # BPSK
    bpsk = generate_bpsk(iq0, 50, 13)
    sdr1.tx([iq0, iq0])  # Send Tx data.

elif MODE == "carrier":

    fs = int(sdr1.sample_rate)
    N = 2**16
    ts = 1 / float(fs)
    t = np.arange(0, N * ts, ts)
    i0 = np.cos(2 * np.pi * t * fc0) * 2**14
    q0 = np.sin(2 * np.pi * t * fc0) * 2**14
    iq0 = i0 + 1j * q0
    sdr1.tx([iq0, iq0])  # Send Tx data.

else:
    print("Not a valid TX Mode....Exiting")
    exit(-1)


xf = np.fft.fftfreq(NumSamples, ts) # Assign frequency bins and "zoom in" to the fc0 signal on those frequency bins
xf = np.fft.fftshift(xf) / 1e6
signal_start = int(NumSamples * (samp_rate / 2 + fc0 / 2) / samp_rate)
signal_end = int(NumSamples * (samp_rate / 2 + fc0 * 2) / samp_rate)

# used to retrieve current data,time
mastClock = datetime.now()  # Master Clock for all comparisons
P1Clock = datetime.now()    # Counts when Pluto 1 begins RX stream 
P2Clock = datetime.now()    # Counts when Pluto 2 Begins RX stream. We need the time_De
print(f'Current mastClock.microsecond: | {mastClock.microsecond}')
print(f'Current P1Clock.microsecond:   | {P1Clock.microsecond}')
print(f'Current P2Clock.microsecond:   | {P2Clock.microsecond}')

''' Collect Data '''
# let each Pluto run for a bit, to do all its calibrations, then get a buffer
for i in range(20):  
    #data1 = sdr1.rx()
    print(f'i = {i}')
    print(f'Before sdr2.rx(): Current P1Clock.second       | {P1Clock.second}')
    print(f'Before sdr2.rx(): Current P2Clock.microsecond: | {P2Clock.microsecond}')
    data2 = sdr2.rx()
    print(f'Before sdr3.rx() / After sdr2.rx(): Current P1Clock.second:       | {P1Clock.second}')
    print(f'Before sdr3.rx() / After sdr2.rx(): Current P2Clock.microsecond:  | {P2Clock.microsecond}')
    data3 = sdr3.rx()
    print(f'After sdr3.rx(): P1Clock.second        | {P1Clock.second}')
    print(f'After sdr3.rx(): P2Clock.microsecond:  | {P2Clock.microsecond}')
    #data4 = sdr4.rx()

''' Calculate and find phase offsets for each Rx node '''
# This assumes the linear array has the P1Tx node set at 0deg to P1Rx1
while(1):
    AVERAGING_PHASE = 15
    #phase_cal_1a = []
    #phase_cal_0b = []
    phase_cal_1b = []
    phase_cal_0c = []
    phase_cal_1c = []
    #phase_cal_0d = []
    #phase_cal_1d = []
    for i in range(AVERAGING_PHASE):
        #data1 = sdr1.rx()
        data2 = sdr2.rx()
        data3 = sdr3.rx()
        #data4 = sdr4.rx()
        
        #Rx_0a = data1[0]        # PlutoSDR 1, RX 0
        #Rx_1a = data1[1]        # PlutoSDR 1, RX 1
        Rx_0b = data2[0]        # PlutoSDR 2, RX 0
        Rx_1b = data2[1]        # PlutoSDR 2, RX 1
        Rx_0c = data3[0]        # PlutoSDR 2, RX 0
        Rx_1c = data3[1]        # PlutoSDR 2, RX 1
        #Rx_0d = data4[0]        # PlutoSDR 2, RX 0
        #Rx_1d = data4[1]        # PlutoSDR 2, RX 1
        #phase_cal_1a.append(compute_phase_offset(Rx_0a, Rx_1a))
        #phase_cal_0b.append(compute_phase_offset(Rx_0b, Rx_1b))
        phase_cal_1b.append(compute_phase_offset(Rx_0b, Rx_1b))
        phase_cal_0c.append(compute_phase_offset(Rx_0b, Rx_0c))
        phase_cal_1c.append(compute_phase_offset(Rx_0b, Rx_1c))

    #phase_cal_1a = int(sum(phase_cal_1a) / len(phase_cal_1a))
    #phase_cal_0b = int(sum(phase_cal_0b) / len(phase_cal_0b))
    phase_cal_1b = int(sum(phase_cal_1b) / len(phase_cal_1b))
    print("Rx 1 Offset: ", phase_cal_1b)
    phase_cal_0c = int(sum(phase_cal_0c) / len(phase_cal_0c))
    print("Rx 2 Offset: ", phase_cal_0c)
    phase_cal_1c = int(sum(phase_cal_1c) / len(phase_cal_1c))
    print("Rx 3 Offset: ", phase_cal_1c)
    #phase_cal_0d = int(sum(phase_cal_1b) / len(phase_cal_1b))
    #phase_cal_1d = int(sum(phase_cal_1b) / len(phase_cal_1b))

''' Scans '''
AVERAGING_SCANS = 1
for i in range(num_scans):
    #data1 = sdr1.rx()
    data2 = sdr2.rx()
    data3 = sdr3.rx()
    #data4 = sdr4.rx()
    # Rx_0a = data1[0]        # PlutoSDR 1, RX 0
    # Rx_1a = data1[1]        # PlutoSDR 1, RX 1
    Rx_0b = data2[0]          # PlutoSDR 2, RX 0
    Rx_1b = data2[1]          # PlutoSDR 2, RX 1
    Rx_0c = data3[0]          # PlutoSDR 3, RX 0
    Rx_1c = data3[1]          # PlutoSDR 3, RX 1
    # Rx_0d = data4[0]        # PlutoSDR 4, RX 0
    # Rx_1d = data4[1]        # PlutoSDR 4, RX 1
    peak_sum = []
    #
    #phase_cal_1a = compute_phase_offset(Rx_0a, Rx_1a)
    #phase_cal_0b = compute_phase_offset(Rx_0a, Rx_0b)
    # phase_cal_1b = compute_phase_offset(Rx_0b, Rx_1b)
    # phase_cal_0c = compute_phase_offset(Rx_0b, Rx_0c)
    # phase_cal_1c = compute_phase_offset(Rx_0b, Rx_1c)
    #phase_cal_0d = compute_phase_offset(Rx_0b, Rx_0d)
    #phase_cal_1d = compute_phase_offset(Rx_0b, Rx_1d)
    #
    delay_phases = np.arange(-180, 180, 2)    # Create an Array for -180 - 180 degrees sweep
    # delay_phases = np.arange(-24, 26, 2)
        
    ''' Phase shift by each degree from -180 to 180 and store peak signal '''
    for phase_delay in delay_phases:   
        peak_sum_avg = []
        for i in range(AVERAGING_SCANS):
            #delayed_Rx_1a = Rx_1a * np.exp(1j * np.deg2rad(1 * phase_delay + phase_cal_1a))
            #delayed_Rx_1a = Rx_1a * np.exp(1j * np.deg2rad(1 * phase_delay + phase_cal_1a))    # PlutoSDR 1 RX 1
            #delayed_Rx_0b = Rx_0b * np.exp(1j * np.deg2rad(3 * phase_delay + phase_cal_1a))    # PlutoSDR 2 RX 0
            delayed_Rx_1b = Rx_1b * np.exp(1j * np.deg2rad(1 * phase_delay + phase_cal_1b))     # PlutoSDR 2 RX 1
            # delayed_Rx_0c = Rx_0c * np.exp(1j * np.deg2rad(1 * phase_delay + phase_cal_0c))     # PlutoSDR 3 RX 0
            # delayed_Rx_1c = Rx_1c * np.exp(1j * np.deg2rad(1 * phase_delay + phase_cal_1c))     # PlutoSDR 3 RX 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          ))    # PlutoSDR 3 RX 1
            #delayed_Rx_0d = Rx_0b * np.exp(1j * np.deg2rad(3 * phase_delay + phase_cal_1a))    # PlutoSDR 4 RX 0
            #delayed_Rx_1d = Rx_1b * np.exp(1j * np.deg2rad(4 * phase_delay + phase_cal_1a))    # PlutoSDR 4 RX 1
            delayed_sum = dbfs( Rx_0b + delayed_Rx_1b ) # + delayed_Rx_0c + delayed_Rx_1c
            peak_sum_avg.append(delayed_sum[signal_start:signal_end])
        peak_sum_value = sum(peak_sum_avg) / len(peak_sum_avg)
        peak_sum.append(np.max(peak_sum_value)) # np.max(delayed_sum[signal_start:signal_end])
    
    peak_dbfs = np.max(peak_sum)
    peak_delay_index = np.where(peak_sum == peak_dbfs)
    peak_delay = delay_phases[peak_delay_index[0][0]]
    steer_angle = int(calcTheta(peak_delay))

    if Plot_Compass == False:
        plt.clf()
        plt.plot(delay_phases, peak_sum)
        plt.axvline(x=peak_delay, color='r', linestyle=':')
        plt.text(-180, -20, f'Peak signal occurs with phase shift = {round(peak_delay,1)} deg')
        #plt.text(-180, -24, f'Phase offset P1_Rx1 = {phase_cal_1a} deg')
        #plt.text(-180, -28, f'Phase offset P2_Rx0 = {phase_cal_0b} deg')
        plt.text(-180, -24, f'Phase offset P2_Rx1 = {phase_cal_1b} deg')
        plt.text(-180, -28, f'Phase offset P1_Rx1 = {phase_cal_0c} deg')
        plt.text(-180, -32, f'Phase offset P2_Rx0 = {phase_cal_1c} deg')
        #plt.text(-180, -32, f'Phase offset P2_Rx1 = {phase_cal_0d} deg')
        #plt.text(-180, -32, f'Phase offset P2_Rx1 = {phase_cal_1d} deg')
        plt.text(-180, -36, f'If d = {int(d*1000)}mm, then steering angle = {steer_angle} deg')
        plt.ylim(top=10, bottom=-100)        
        plt.xlabel("phase shift [deg]")
        plt.ylabel("P1_Rx0 + P1_Rx1 + P2_Rx0 + P2_Rx1 [dBfs]")
        plt.draw()
        plt.pause(0.05)
        time.sleep(0.1)

    else:
        plt.clf()
        fig = plt.figure(figsize=(3,3))
        ax = plt.subplot(111, polar=True)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetamin(-90)
        ax.set_thetamax(90)
        ax.set_rlim(bottom=-20, top=0)
        ax.set_yticklabels([])
        # ax.vlines(np.deg2rad(steer_angle_0b), 0, -20)
        # ax.vlines(np.deg2rad(steer_angle_1a), 0, -20)
        # ax.vlines(np.deg2rad(steer_angle_1b), 0, -20)
        # ax.text(-2, -12, f'P1 RX1 Steering Angle: {steer_angle_0b} deg')
        # ax.text(-2, -14, f'P2 RX0 Steering Angle: {steer_angle_1a} deg')
        # ax.text(-2, -16, f'P2 RX1 Steering Angle: {steer_angle_1b} deg')
        plt.draw()
        plt.pause(0.05)
        time.sleep(0.1)

plt.show()

sdr1.tx_destroy_buffer()