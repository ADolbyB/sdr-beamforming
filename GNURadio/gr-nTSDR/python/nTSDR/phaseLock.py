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

class phaseLock(gr.hier_block2):
    """
    docstring for block phaseLock
    """
    def __init__(self, 
                 num_channels=2):
        gr.hier_block2.__init__(self,
            "phaseLock",
            gr.io_signature(0,0,0),  # Input signature
            gr.io_signature(num_channels, num_channels, gr.sizeof_gr_complex) # Output signature
        )
        # Self-Assign Variables
        self.num_channels = num_channels
        self.delays = {}

        # Block Creation
        self.phase_amplitude_corrections = {}        
        self.phase_and_amplitude_correctors = {}
        self.sdr_sources = {}
        self.delay_blocks = {}
        self.vsinks = {}

        for inp in range(0, num_channels):
            self.connect((self, inp), (self, inp)) # Input straight to Output [test only]
