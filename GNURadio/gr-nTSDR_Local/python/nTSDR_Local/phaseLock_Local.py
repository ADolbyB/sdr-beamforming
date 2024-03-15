#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 nTSDR.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr
from gnuradio import blocks
import numpy as np
from numpy import *
from pylab import *
import math
import time
import threading

def xcorrelate(X,Y,maxlag):
    N = max(len(X),len(Y))
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

class phaseAdjust(gr.sync_block):
    def __init__(self, phase_angle=0):
        gr.sync_block.__init__(self,
            name="Phase Adjust", 
            in_sig=[(gr.sizeof_gr_complex,)], 
            out_sig=[(gr.sizeof_gr_complex,)])
        self.phase_angle = phase_angle

    def work(self, input_items, output_items):
        # phase_shift = np.exp(1j*np.deg2rad(self.phase_angle))
        phase_shift = self.phase_angle
        output_items[0][:] = input_items[0] * phase_shift
        return len(output_items[0])
    
    def set_phase(self, phase_angle):
        print("Phase angle set to ", phase_angle)
        self.phase_angle = phase_angle
        

class storageBlock(gr.sync_block):
    def __init__(self, thresh=1027*4):
        gr.sync_block.__init__(
            self, 
            name="Data Storage",
            in_sig=[(gr.sizeof_gr_complex, 1027)], 
            out_sig=[])
        self.data = []
        self.threshold = thresh
        self.full_storage = False

    def work(self, input_items, output_items):
        # check if samples have surpassed threshold
        if len(self.data) < self.threshold:
            self.data.extend(input_items[0])
        else:
            self.full_storage = True
        return(len(input_items[0]))
    
    def get_data(self):
        return np.array(self.data)
    
    def get_fullness(self):
        return self.full_storage

class phaseLock_Local(gr.hier_block2):
    """
    Synchronize the phase of homogenous IQ streams.
    """
    def __init__(self, 
                 num_channels=2):
        gr.hier_block2.__init__(self,
            "Phase Lock Local",
            gr.io_signature(num_channels, num_channels, gr.sizeof_gr_complex),  # Input signature
            gr.io_signature(num_channels, num_channels, gr.sizeof_gr_complex) # Output signature
        )
        # Self-Assign Variables
        self.num_channels = num_channels
        self.fullness = 0
        self.delays = {}
        self.phase_amplitude_corrections = {}  
        #
        self.state = "wait" # wait -> sync -> work

        # Block Creation    
        self.phase_and_amplitude_correctors = {}
        self.delay_blocks = {}
        self.data_sinks = {}

        for chan in range(0, num_channels):

            # Assign Blocks
            self.data_sinks[chan] = storageBlock()
            self.delay_blocks[chan] = blocks.delay(gr.sizeof_gr_complex*1, 0)
            self.phase_amplitude_corrections[chan]=0
            self.phase_and_amplitude_correctors[chan] = phaseAdjust()
            # self.phase_and_amplitude_correctors[chan] = blocks.multiply_const_vcc((self.phase_amplitude_corrections[chan], ))

            # Connect Blocks
            self.connect((self, chan), (self.data_sinks[chan], 0))
            self.connect((self, chan), (self.delay_blocks[chan], 0))
            self.connect((self.delay_blocks[chan], 0), (self.phase_and_amplitude_correctors[chan], 0))
            self.connect((self.phase_and_amplitude_correctors[chan], 0), (self, chan))

        # Begin periodic check
        checkThread = threading.Thread(target=self.continous_check, daemon=True)
        checkThread.start()

    def continous_check(self):
        while self.state == "wait":
            self.check_for_fullness()
            time.sleep(1)

    def check_for_fullness(self):
        print("#")
        fullness_count = 0
        for chan in range(0, self.num_channels):
            if self.data_sinks[chan].get_fullness()==True:
                fullness_count += 1
                print("Channel ", chan, " full")
            else: break

        # Call sync if all channels are full
        if fullness_count==self.num_channels:
            self.state="sync"
            self.compute_and_set_delays()

    def compute_and_set_delays(self):
        print("\n")
        print("#-#-#-#-# SYNC PROCESS STARTED #-#-#-#-#")
        print("\n")

        # Initial Values
        self.delays[0] = 0
        self.phase_amplitude_corrections[0]=0

        for chan in range(1,self.num_channels):
            ref_data = self.data_sinks[0].get_data()
            rx_data = self.data_sinks[chan].get_data()
            var0=var(ref_data)
            varR=var(rx_data)
            result_corr = xcorrelate(ref_data, ref_data, 
                                    int(len(ref_data)/2)) 
                                    #resize(rx_data, ref_data)
            max_position = argmax(abs(result_corr))
            self.delays[chan] = len(result_corr)/2-max_position

            # Phase Corrections
            self.phase_amplitude_corrections[chan] = result_corr[max_position]/sqrt(mean(real(self.data_sinks[chan].get_data())**2+imag(self.data_sinks[chan].get_data())**2))
            phase_angle = angle(self.phase_amplitude_corrections[chan])/pi*180
            #
            # self.phase_amplitude_corrections[chan] = angle(self.phase_amplitude_corrections[chan])/pi*180
            #
            # self.phase_and_amplitude_correctors[chan].set_phase(self.phase_amplitude_corrections[chan])
            #
            self.phase_and_amplitude_correctors[chan].set_phase(sqrt(var0/varR)*(exp(1j*angle(self.phase_amplitude_corrections[chan]))))
            #
            # self.phase_and_amplitude_correctors[chan].set_k((sqrt(var0/var(self.data_sinks[chan].get_data()))*(exp(1j*angle(self.phase_amplitude_corrections[chan]))),))

        #set delays
        for chan in range(0,self.num_channels):        
            print ("Delay of channel ",chan,": ",self.delays[chan],' phase diff: ', phase_angle, " [deg]")
            self.delay_blocks[chan].set_dly(-int(self.delays[chan]))
        
        self.state = "work"