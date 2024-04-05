'''Simple script to test and display Barker Sequences with BPSK'''
# Peyton Adkins

import adi
import matplotlib.pyplot as plt
import numpy as np
import pylab as pl
import math
import time
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

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
def xcorrelate(X,Y,maxlag):
    N = max(len(X), len(Y))
    N_nextpow2 = math.ceil(math.log(N + maxlag,2))
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

def calcTheta(phase):
    # calculates the steering angle for a given phase delta (phase is in deg)
    # steering angle is theta = arcsin(c * deltaphase / (2 * pi * f * d)
    arcsin_arg = np.deg2rad(phase) * 3e8 / (2 * np.pi * rx_lo * d)
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
phase_cal = -52

''' Set distance between Rx antennas '''
d_wavelength = 0.5                  # distance between elements as a fraction of wavelength.  This is normally 0.5
wavelength = 3e8 / rx_lo            # wavelength of the RF carrier
d = d_wavelength * wavelength       # distance between elements in meters
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

# Barker Sequence
b13 = np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1])

'''Program Tx and Send Data'''
fs = int(sdr.sample_rate)
N = 2**4
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i0 = np.cos(2 * np.pi * t * fc0) * 2 ** 14
q0 = np.sin(2 * np.pi * t * fc0) * 2 ** 14
iq0 = i0 + 1j * q0

# BPSK
x = np.hstack((np.zeros(5), b13, iq0, np.zeros(5)))

bpsk = generate_bpsk(x, 50, 13)

plt.plot(np.arange(bpsk.size), bpsk)
# plt.ylim(top=10, bottom=-100)        
plt.xlabel("magnitude")
plt.ylabel("sample time indices")
plt.draw()
plt.show()

bpsk = x

sdr.tx([bpsk, bpsk])                           # Send Tx data.

# NOTE: Frequency bins may be of different length than that of the BPSK data

xf = np.fft.fftfreq(NumSamples, ts) # Assign frequency bins and "zoom in" to the fc0 signal on those frequency bins
xf = np.fft.fftshift(xf) / 1e6
signal_start = int(NumSamples * (samp_rate / 2 + fc0 / 2) / samp_rate)
signal_end = int(NumSamples * (samp_rate / 2 + fc0 * 2) / samp_rate)

''' Scans '''
AVERAGING_SCANS = 1
for i in range(25):
    data1 = sdr.rx()
    # data2 = sdr2.rx()
    # data3 = sdr3.rx()
    # data4 = sdr4.rx()
    Rx_0a = data1[0]        # PlutoSDR 1, RX 0
    Rx_1a = data1[1]        # PlutoSDR 1, RX 1
    # Rx_0b = data2[0]        # PlutoSDR 2, RX 0
    # Rx_1b = data2[1]        # PlutoSDR 2, RX 1
    # Rx_0c = data3[0]      # PlutoSDR 3, RX 0
    # Rx_1c = data3[1]      # PlutoSDR 3, RX 1
    # Rx_0d = data4[0]      # PlutoSDR 4, RX 0
    # Rx_1d = data4[1]      # PlutoSDR 4, RX 1
    peak_sum = []
    #
    phase_cal_1a = compute_phase_offset(Rx_0a, Rx_1a)
    # phase_cal_0b = compute_phase_offset(Rx_0a, Rx_0b)
    # phase_cal_1b = compute_phase_offset(Rx_0a, Rx_1b)
    #
    delay_phases = np.arange(-180, 180, 2)    # Create an Array for -180 - 180 degrees sweep
        
    '''Phase shift by each degree from -180 to 180 and store peak signal'''
    for phase_delay in delay_phases:   
        peak_sum_avg = []
        for i in range(AVERAGING_SCANS):
            delayed_Rx_1a = Rx_1a * np.exp(1j * np.deg2rad(1 * phase_delay + phase_cal_1a))    # PlutoSDR 1 RX 1
            # delayed_Rx_0b = Rx_0b * np.exp(1j * np.deg2rad(2 * phase_delay + phase_cal_1a))    # PlutoSDR 2 RX 0
            # delayed_Rx_1b = Rx_1b * np.exp(1j * np.deg2rad(3 * phase_delay + phase_cal_1a))    # PlutoSDR 2 RX 1
            delayed_sum = dbfs(Rx_0a + delayed_Rx_1a) #+ delayed_Rx_0b + delayed_Rx_1b
            peak_sum_avg.append(delayed_sum[signal_start:signal_end])
        peak_sum_value = sum(peak_sum_avg) / len(peak_sum_avg)
        peak_sum.append(np.max(peak_sum_value)) # np.max(delayed_sum[signal_start:signal_end])
    
    peak_dbfs = np.max(peak_sum)
    peak_delay_index = np.where(peak_sum == peak_dbfs)
    peak_delay = delay_phases[peak_delay_index[0][0]]
    steer_angle = int(calcTheta(peak_delay))

    plt.clf()
    plt.plot(delay_phases, peak_sum)
    plt.axvline(x=peak_delay, color='r', linestyle=':')
    plt.text(-180, -20, f'Peak signal occurs with phase shift = {round(peak_delay,1)} deg')
    plt.text(-180, -24, f'Phase offset P1_Rx1 = {phase_cal_1a} deg')
    # plt.text(-180, -28, f'Phase offset P2_Rx0 = {phase_cal_0b} deg')
    # plt.text(-180, -32, f'Phase offset P2_Rx1 = {phase_cal_1b} deg')
    plt.text(-180, -36, f'If d = {int(d*1000)}mm, then steering angle = {steer_angle} deg')
    plt.ylim(top=10, bottom=-100)        
    plt.xlabel("phase shift [deg]")
    plt.ylabel("P1_Rx0 + P1_Rx1 + P2_Rx0 + P2_Rx1 [dBfs]")
    plt.draw()
    plt.pause(0.05)
    time.sleep(0.1)

plt.show()