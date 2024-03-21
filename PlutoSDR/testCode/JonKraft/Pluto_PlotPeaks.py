'''
Joel Brigida & Peyton Adkins
Modified Plot Peaks Code for Testing multiple PlutoSDR units simultaneously.
All modifications are ours: Copyright 2023 Joel Brigida & Peyton Adkins
'''
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
#       on or directly connected to an Analog Devices Inc. component.

'''
JB: Valid USA ISM Bands: https://en.wikipedia.org/wiki/ISM_radio_band
Note that ISM bands in the USA do not require a license to operate on.
The original PlotPeaks used 2.3 GHz which is outside of the ISM band.
These ISM bands should work with a TX modified PlutoSDR, please use RESPONSIBLY.
40.66 MHz - 40.7 MHz
433.05 MHz - 434.79 MHz
902 MHz - 928 MHz
2.4 GHz - 2.5 GHz
5.725 GHz - 5.875 GHz
'''

from sys import path
print(f'sys.path = {path}')     # Edit JB: may need to add path to PYTHONPATH for OSError: [Errno 16] Device or resource busy

from adi import ad9361
import matplotlib.pyplot as plt
import numpy as np
import time

''' Setup '''
samp_rate = 2e6                     # 2e6 = 2MHz: must be <=30.72 MHz if both channels are enabled
NumSamples = 2**12
rx_lo = 2.45e9                      # 2.45GHz (Keep it inside the USA ISM band: 2.4GHz - 2.5GHz)
rx_mode = "manual"                  # can be "manual" or "slow_attack"
rx_gain0 = 40
rx_gain1 = 40
tx_lo = rx_lo
tx_gain = -3
fc0 = int(200e3)
phase_cal = 92
num_scans = 500
Plot_Compass = False

''' Set distance between Rx antennas '''
d_wavelength = 0.5                  # distance between elements as a fraction of wavelength.  This is normally 0.5
wavelength = 3E8 / rx_lo            # wavelength of the RF carrier
d = d_wavelength * wavelength       # distance between elements in meters
print("Set distance between Rx Antennas to ", int(d * 1000), "mm")

''' Create Radio '''
sdr1 = ad9361(uri='ip:192.168.2.1') # Pluto #1
sdr2 = ad9361(uri='ip:192.168.3.1') # Pluto #2
#sdr3 = ad9361(uri='ip:192.168.4.1') # Pluto #3
#sdr4 = ad9361(uri='ip:192.168.5.1') # Pluto #4


''' Configure All PlutoSDR Radio Channels '''
sdr1.rx_enabled_channels = [0, 1]
sdr2.rx_enabled_channels = [0, 1]
# sdr3.rx_enabled_channels = [0, 1]
# sdr4.rx_enabled_channels = [0, 1]
sdr1.sample_rate = int(samp_rate)
sdr2.sample_rate = int(samp_rate)
# sdr3.sample_rate = int(samp_rate)
# sdr4.sample_rate = int(samp_rate)
sdr1.rx_rf_bandwidth = int(fc0 * 3)
sdr2.rx_rf_bandwidth = int(fc0 * 3)
# sdr3.rx_rf_bandwidth = int(fc0 * 3)
# sdr4.rx_rf_bandwidth = int(fc0 * 3)
sdr1.rx_lo = int(rx_lo)
sdr2.rx_lo = int(rx_lo)
# sdr3.rx_lo = int(rx_lo)
# sdr4.rx_lo = int(rx_lo)
sdr1.gain_control_mode = rx_mode
sdr2.gain_control_mode = rx_mode
# sdr3.gain_control_mode = rx_mode
# sdr4.gain_control_mode = rx_mode
sdr1.rx_hardwaregain_chan0 = int(rx_gain0)
sdr2.rx_hardwaregain_chan0 = int(rx_gain0)
# sdr3.rx_hardwaregain_chan0 = int(rx_gain0)
# sdr4.rx_hardwaregain_chan0 = int(rx_gain0)
sdr1.rx_hardwaregain_chan1 = int(rx_gain1)
sdr2.rx_hardwaregain_chan1 = int(rx_gain1)
# sdr3.rx_hardwaregain_chan1 = int(rx_gain1)
# sdr4.rx_hardwaregain_chan1 = int(rx_gain1)
sdr1.rx_buffer_size = int(NumSamples)
sdr2.rx_buffer_size = int(NumSamples)
# sdr3.rx_buffer_size = int(NumSamples)
# sdr4.rx_buffer_size = int(NumSamples)
sdr1._rxadc.set_kernel_buffers_count(1)     # set buffers to 1 (instead of the default 4) to avoid stale data on Pluto
sdr2._rxadc.set_kernel_buffers_count(1)
# sdr3._rxadc.set_kernel_buffers_count(1)
# sdr4._rxadc.set_kernel_buffers_count(1)
sdr1.tx_rf_bandwidth = int(fc0 * 3)         # ONLY TX 1 of PlutoSDR 1 will have TX capability.
sdr1.tx_lo = int(tx_lo)
sdr1.tx_cyclic_buffer = True
sdr1.tx_hardwaregain_chan0 = int(tx_gain)   # ONLY TX1 of PlutoSDR 1 is the transmitter.
sdr2.tx_hardwaregain_chan0 = int(-88)       # Shut Off all other TX Channels for all Plutos
# sdr3.tx_hardwaregain_chan0 = int(-88)
# sdr4.tx_hardwaregain_chan0 = int(-88)
sdr1.tx_hardwaregain_chan1 = int(-88)
sdr2.tx_hardwaregain_chan1 = int(-88)
# sdr3.tx_hardwaregain_chan1 = int(-88)
# sdr4.tx_hardwaregain_chan1 = int(-88)
sdr1.tx_buffer_size = int(2 ** 18)

''' Program SDR1 TX1 and Send Data From PlutoSDR 1 to all other RX Nodes '''
fs = int(sdr1.sample_rate)
N = 2 ** 16
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i0 = np.cos(2 * np.pi * t * fc0) * 2 ** 14
q0 = np.sin(2 * np.pi * t * fc0) * 2 ** 14
iq0 = i0 + 1j * q0
sdr1.tx([iq0, iq0])  # Send Tx data.

xf = np.fft.fftfreq(NumSamples, ts) # Assign frequency bins and "zoom in" to the fc0 signal on those frequency bins
xf = np.fft.fftshift(xf) / 1e6
signal_start = int(NumSamples * (samp_rate / 2 + fc0 / 2) / samp_rate)
signal_end = int(NumSamples * (samp_rate / 2 + fc0 * 2) / samp_rate)

def calcTheta(phase):
    # calculates the steering angle for a given phase delta (phase is in deg)
    # steering angle is theta = arcsin(c * deltaphase / (2 * pi * f * d)
    arcsin_arg = np.deg2rad(phase) * 3E8 / (2 * np.pi * rx_lo * d)
    arcsin_arg = max(min(1, arcsin_arg), -1) # arcsin argument must be between 1 and -1, or numpy will throw a warning
    calc_theta = np.rad2deg(np.arcsin(arcsin_arg))
    return calc_theta

def dbfs(raw_data):
    # function to convert IQ samples to FFT plot, scaled in dBFS
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20 * np.log10(np.abs(s_shift) / (2**11))     # Pluto is a signed 12 bit ADC, so use 2^11 to convert to dBFS
    return s_dbfs

''' Collect Data '''
for i in range(20):  
    # let Pluto run for a bit, to do all its calibrations, then get a buffer
    data1 = sdr1.rx()
    data2 = sdr2.rx()
    # data3 = sdr3.rx()
    # data4 = sdr4.rx()

for i in range(num_scans):
    data1 = sdr1.rx()
    data2 = sdr2.rx()
    # data3 = sdr3.rx()
    # data4 = sdr4.rx()
    Rx_0a = data1[0]        # PlutoSDR 1, RX 0
    Rx_1a = data1[1]        # PlutoSDR 1, RX 1
    Rx_0b = data2[0]        # PlutoSDR 2, RX 0
    Rx_1b = data2[1]        # PlutoSDR 2, RX 1
    # Rx_0c = data3[0]      # PlutoSDR 3, RX 0
    # Rx_1c = data3[1]      # PlutoSDR 3, RX 1
    # Rx_0d = data4[0]      # PlutoSDR 4, RX 0
    # Rx_1d = data4[1]      # PlutoSDR 4, RX 1
    peak_sum_1a = []
    peak_sum_0b = []
    peak_sum_1b = []
    
    delay_phases = np.arange(-180, 180, 2)    # Create an Array for -180 - 180 degrees sweep
    
    for phase_delay in delay_phases:   
        delayed_Rx_1a = Rx_1a * np.exp(1j * np.deg2rad(phase_delay + phase_cal))    # PlutoSDR 1 RX 1
        delayed_Rx_0b = Rx_1a * np.exp(1j * np.deg2rad(phase_delay + phase_cal))    # PlutoSDR 2 RX 0
        delayed_Rx_1b = Rx_1a * np.exp(1j * np.deg2rad(phase_delay + phase_cal))    # PlutoSDR 2 RX 1
        delayed_sum_rx_1a = dbfs(Rx_0a + delayed_Rx_1a)      # PlutoSDR 1 RX 1
        delayed_sum_rx_0b = dbfs(Rx_0b + delayed_Rx_0b)      # PlutoSDR 2 RX 0
        delayed_sum_rx_1b = dbfs(Rx_1b + delayed_Rx_1b)      # PlutoSDR 2 RX 1
        peak_sum_1a.append(np.max(delayed_sum_rx_1a[signal_start:signal_end]))
        peak_sum_0b.append(np.max(delayed_sum_rx_0b[signal_start:signal_end]))
        peak_sum_1b.append(np.max(delayed_sum_rx_1b[signal_start:signal_end]))
    
    peak_dbfs_1a = np.max(peak_sum_1a)
    peak_dbfs_0b = np.max(peak_sum_0b)
    peak_dbfs_1b = np.max(peak_sum_1b)
    
    peak_delay_index_1a = np.where(peak_sum_1a == peak_dbfs_1a)
    peak_delay_index_0b = np.where(peak_sum_0b == peak_dbfs_0b)
    peak_delay_index_1b = np.where(peak_sum_1b == peak_dbfs_1b)
    
    peak_delay_1a = delay_phases[peak_delay_index_1a[0][0]]
    peak_delay_0b = delay_phases[peak_delay_index_0b[0][0]]
    peak_delay_1b = delay_phases[peak_delay_index_1b[0][0]]
    
    ## TODO: There maybe an add'l function needed to average the peak delays here

    steer_angle_1a = int(calcTheta(peak_delay_1a))
    steer_angle_0b = int(calcTheta(peak_delay_0b))
    steer_angle_1b = int(calcTheta(peak_delay_1b))

    ## TODO: Can we just average the steering angles here? May need add'l logic here

    if Plot_Compass == False:
        plt.clf()
        plt.plot(delay_phases, peak_sum_1a)     # PlutoSDR 1 RX 1
        plt.plot(delay_phases, peak_sum_0b)     # PlutoSDR 2 RX 0
        plt.plot(delay_phases, peak_sum_1b)     # PlutoSDR 2 RX 1
        plt.axvline(x = peak_delay_1a, color='r', linestyle=':')    # PlutoSDR 1 RX 1
        plt.axvline(x = peak_delay_0b, color='g', linestyle=':')    # PlutoSDR 2 RX 0
        plt.axvline(x = peak_delay_1b, color='b', linestyle=':')    # PlutoSDR 2 RX 1
        plt.text(-180, -22, f'Peak signal 1a occurs with phase shift = {format(round(peak_delay_1a, 1))} deg')
        plt.text(-180, -24, f'Peak signal 0b occurs with phase shift = {format(round(peak_delay_0b, 1))} deg')
        plt.text(-180, -26, f'Peak signal 1b occurs with phase shift = {format(round(peak_delay_1b, 1))} deg')
        plt.text(-180, -28, f'RX 1A: If d = {int(d * 1000)}mm, then steering angle = {steer_angle_1a} deg')
        plt.text(-180, -30, f'RX 0B: If d = {int(d * 1000)}mm, then steering angle = {steer_angle_0b} deg')
        plt.text(-180, -32, f'RX 1B: If d = {int(d * 1000)}mm, then steering angle = {steer_angle_1b} deg')
        plt.ylim(top = 0, bottom = -34)
        plt.xlabel("Phase Shift [deg]")
        plt.ylabel("Rx0 + Rx1 [dBfs]")
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
        ax.vlines(np.deg2rad(steer_angle_0b), 0, -20)
        ax.vlines(np.deg2rad(steer_angle_1a), 0, -20)
        ax.vlines(np.deg2rad(steer_angle_1b), 0, -20)
        ax.text(-2, -12, f'P1 RX1 Steering Angle: {steer_angle_0b} deg')
        ax.text(-2, -14, f'P2 RX0 Steering Angle: {steer_angle_1a} deg')
        ax.text(-2, -16, f'P2 RX1 Steering Angle: {steer_angle_1b} deg')
        plt.draw()
        plt.pause(0.05)
        time.sleep(0.1)

plt.show()

sdr1.tx_destroy_buffer()