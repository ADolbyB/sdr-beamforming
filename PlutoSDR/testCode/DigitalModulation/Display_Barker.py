'''Simple script to test and display Barker Sequences with BPSK'''
# Peyton Adkins

import matplotlib.pyplot as plt
import numpy as np
import pylab as pl
import math
import time

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

# Setup
samp_rate = 2e6   

# Barker Sequence
b13 = np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1])

# Carrier Signal
fc0 = int(200e3)
fs = int(samp_rate)
N = 2**6 #2**16
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i0 = np.cos(2 * np.pi * t * fc0) * 2**2 #2**14
q0 = np.sin(2 * np.pi * t * fc0) * 2**2
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