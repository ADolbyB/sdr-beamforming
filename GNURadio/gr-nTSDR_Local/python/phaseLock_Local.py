#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Peyton.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from gnuradio import gr
from gnuradio import blocks
import threading
import nTSDR_Local

# Definition via Piotr Krysik
class vector_sink_fullness_notifier(gr.feval):
    """
    This class allows C++ code to callback into python.
    """
    def __init__(self, b):
        gr.feval.__init__(self)
        self.b = b
        self.d_mutex = threading.Lock()

    def eval(self):
        """
        This method is called by vector_sink_cn when it is full
        """
        self.d_mutex.acquire()
        try:
            self.b.fullness_report()
        except Exception as e:
            print("Vector sink fullness notification exception: ", e)
        finally:
            self.d_mutex.release()

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
        self.delays = {}
        self.phase_amplitude_corrections = {}  
        #
        self.state = "sync"

        # Block Creation    
        self.phase_and_amplitude_correctors = {}
        self.delay_blocks = {}
        self.vsinks = {}

        # Vector Sink Fullness Alert
        # self.vsink_notifier = vector_sink_fullness_notifier(self) # provides a callback function for when vector sinks are full -Piotr Krysik

        for chan in range(0, num_channels):
            # Assign Blocks
            self.delay_blocks[chan] = blocks.delay(gr.sizeof_gr_complex*1, 0)
            self.phase_amplitude_corrections[chan]=1.0
            self.phase_and_amplitude_correctors[chan] = blocks.multiply_const_vcc((self.phase_amplitude_corrections[chan], ))

            # Connect Blocks
            self.connect((self, chan), (self.delay_blocks[chan], 0))
            self.connect((self.delay_blocks[chan], 0), (self.phase_and_amplitude_correctors[chan], 0))
            self.connect((self.phase_and_amplitude_correctors[chan], 0), (self, chan))
