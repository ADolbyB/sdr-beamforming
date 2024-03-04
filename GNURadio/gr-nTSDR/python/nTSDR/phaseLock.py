#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 nTSDR.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation: either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY: without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software: see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
from gnuradio import blocks

class phaseLock(gr.hier_block2):
    """
    Synchronize the phase of homogenous IQ streams.
    """
    def __init__(self, 
                 num_channels=2):
        gr.hier_block2.__init__(self,
            "Phase Sync",
            gr.io_signature(num_channels, num_channels, gr.sizeof_gr_complex),  # Input signature
            gr.io_signature(num_channels, num_channels, gr.sizeof_gr_complex) # Output signature
        )
        # Self-Assign Variables
        self.num_channels = num_channels
        self.delays = {}
        self.phase_amplitude_corrections = {}  

        # Block Creation    
        self.phase_and_amplitude_correctors = {}
        self.delay_blocks = {}
        self.vsinks = {}

        for chan in range(0, num_channels):
            # Assign Blocks
            self.delay_blocks[chan] = blocks.delay(gr.sizeof_gr_complex*1, 0)
            self.phase_amplitude_corrections[chan]=1.0
            self.phase_and_amplitude_correctors[chan] = blocks.multiply_const_vcc((self.phase_amplitude_corrections[chan], ))

            # Connect Blocks
            self.connect((self, chan), (self.delay_blocks[chan], 0))
            self.connect((self.delay_blocks[chan], 0), (self.phase_and_amplitude_correctors[chan], 0))
            self.connect((self.phase_and_amplitude_correctors[chan], 0), (self, chan))
