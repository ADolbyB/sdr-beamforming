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
print(f'sys.path = {sys.path}')     # Edit JB: may need to add path to PYTHONPATH for OSError: [Errno 16] Device or resource busy

import adi
import matplotlib.pyplot as plt
import numpy as np
from numpy import *
from pylab import *
import time
import math

## The following addition is not written by Jon Kraft and serves to test cross-correlation calculations potentially used for estimating phase offsets between Rx nodes

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

    # print ("Delay of ", Rx_name, ": ", delay,' | Phase Diff: ', phase_diff, " [deg]")

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
    return phase_diff, delay

'''Setup'''
samp_rate = 2e6                     # must be <=30.72 MHz if both channels are enabled
NumSamples = 2**12
rx_lo = 2.3e9
rx_mode = "manual"  # can be "manual" or "slow_attack"
rx_gain0 = 40
rx_gain1 = 40
tx_lo = rx_lo
tx_gain = -3
fc0 = int(200e3)
phase_cal = 0
num_scans = 500
Plot_Compass = False

''' Set distance between Rx antennas '''
d_wavelength = 0.5                  # distance between elements as a fraction of wavelength.  This is normally 0.5
wavelength = 3E8/rx_lo              # wavelength of the RF carrier
d = d_wavelength*wavelength         # distance between elements in meters
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
sdr._rxadc.set_kernel_buffers_count(1)   # set buffers to 1 (instead of the default 4) to avoid stale data on Pluto
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
sdr.tx([iq0,iq0])  # Send Tx data.

xf = np.fft.fftfreq(NumSamples, ts) # Assign frequency bins and "zoom in" to the fc0 signal on those frequency bins
xf = np.fft.fftshift(xf)/1e6
signal_start = int(NumSamples*(samp_rate/2+fc0/2)/samp_rate)
signal_end = int(NumSamples*(samp_rate/2+fc0*2)/samp_rate)

def calcTheta(phase):
    # calculates the steering angle for a given phase delta (phase is in deg)
    # steering angle is theta = arcsin(c*deltaphase/(2*pi*f*d)
    arcsin_arg = np.deg2rad(phase)*3E8/(2*np.pi*rx_lo*d)
    arcsin_arg = max(min(1, arcsin_arg), -1)     # arcsin argument must be between 1 and -1, or numpy will throw a warning
    calc_theta = np.rad2deg(np.arcsin(arcsin_arg))
    return calc_theta

def dbfs(raw_data):
    # function to convert IQ samples to FFT plot, scaled in dBFS
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20*np.log10(np.abs(s_shift)/(2**11))     # Pluto is a signed 12 bit ADC, so use 2^11 to convert to dBFS
    return s_dbfs

'''Collect Data'''
for i in range(20):  
    # let Pluto run for a bit, to do all its calibrations, then get a buffer
    data = sdr.rx()

for i in range(num_scans):
    data = sdr.rx()
    Rx_0=data[0]
    Rx_1=data[1]
    phase_diff, calc_delay = compute_and_set_delay(Rx_0, Rx_1, "Rx_1", samp_rate)
    peak_sum = []
    delay_phases = np.arange(-180, 180, 2)    # phase delay in degrees
    for phase_delay in delay_phases:   
        delayed_Rx_1 = Rx_1 * np.exp(1j*np.deg2rad(phase_delay+phase_cal))
        delayed_sum = dbfs(Rx_0 + delayed_Rx_1)
        peak_sum.append(np.max(delayed_sum[signal_start:signal_end]))
    peak_dbfs = np.max(peak_sum)
    peak_delay_index = np.where(peak_sum==peak_dbfs)
    peak_delay = delay_phases[peak_delay_index[0][0]]
    steer_angle = int(calcTheta(peak_delay))
    if Plot_Compass==False:
        plt.clf()
        plt.plot(delay_phases, peak_sum)
        plt.axvline(x=peak_delay, color='r', linestyle=':')
        plt.text(-180, -22, "Peak signal occurs with phase shift = {} deg".format(round(peak_delay,1)))
        plt.text(-180, -24, "Calculated phase offset = {} deg".format(int(phase_diff)))
        plt.text(-180, -26, "Calculated delay = {}".format(int(calc_delay)))
        plt.text(-180, -28, "If d={}mm, then steering angle = {} deg".format(int(d*1000), steer_angle))
        plt.ylim(top=0, bottom=-30)        
        plt.xlabel("phase shift [deg]")
        plt.ylabel("Rx0 + Rx1 [dBfs]")
        plt.draw()
        plt.pause(0.05)
        time.sleep(0.1)
        # plt.show()
    else:
        plt.clf()
        fig = plt.figure(figsize=(3,3))
        ax = plt.subplot(111,polar=True)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetamin(-90)
        ax.set_thetamax(90)
        ax.set_rlim(bottom=-20, top=0)
        ax.set_yticklabels([])
        ax.vlines(np.deg2rad(steer_angle),0,-20)
        ax.text(-2, -14, "{} deg".format(steer_angle))
        plt.draw()
        plt.pause(0.05)
        time.sleep(0.1)
        # plt.show()

plt.show()

sdr.tx_destroy_buffer()
if i > 40: print('\a')    # for a long capture, beep when the script is done