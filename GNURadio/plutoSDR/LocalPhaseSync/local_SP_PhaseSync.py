#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Local Single Pluto Phase Sync
# Author: Peyton
# GNU Radio version: 3.10.7.0

from packaging.version import Version as StrictVersion
from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio



class local_SP_PhaseSync(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Local Single Pluto Phase Sync", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Local Single Pluto Phase Sync")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "local_SP_PhaseSync")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2000000
        self.pluto1 = pluto1 = "ip:192.168.2.1"
        self.freq = freq = 100000000
        self.baseband = baseband = 500
        self.Tx1_path = Tx1_path = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/LocalPhaseSync/fileOutputTx1"
        self.Rx2_path = Rx2_path = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/LocalPhaseSync/fileOutputRx2"
        self.Rx1_path = Rx1_path = "/home/ubuntu/PlutoSDR/sdr-beamforming/GNURadio/plutoSDR/LocalPhaseSync/fileOutputRx1"

        ##################################################
        # Blocks
        ##################################################

        self.low_pass_filter_1 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                5000,
                2000,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                5000,
                2000,
                window.WIN_HAMMING,
                6.76))
        self.iio_fmcomms2_source_0 = iio.fmcomms2_source_fc32(pluto1, [True, True, True, True], 32768)
        self.iio_fmcomms2_source_0.set_len_tag_key('packet_len')
        self.iio_fmcomms2_source_0.set_frequency(freq)
        self.iio_fmcomms2_source_0.set_samplerate(samp_rate)
        if True:
            self.iio_fmcomms2_source_0.set_gain_mode(0, 'manual')
            self.iio_fmcomms2_source_0.set_gain(0, 64)
        if True:
            self.iio_fmcomms2_source_0.set_gain_mode(1, 'manual')
            self.iio_fmcomms2_source_0.set_gain(1, 64)
        self.iio_fmcomms2_source_0.set_quadrature(True)
        self.iio_fmcomms2_source_0.set_rfdc(True)
        self.iio_fmcomms2_source_0.set_bbdc(True)
        self.iio_fmcomms2_source_0.set_filter_params('Auto', '', 0, 0)
        self.iio_fmcomms2_sink_0 = iio.fmcomms2_sink_fc32(pluto1, [True, True, False, False], 32768, False)
        self.iio_fmcomms2_sink_0.set_len_tag_key('')
        self.iio_fmcomms2_sink_0.set_bandwidth(20000000)
        self.iio_fmcomms2_sink_0.set_frequency(freq)
        self.iio_fmcomms2_sink_0.set_samplerate(samp_rate)
        if True:
            self.iio_fmcomms2_sink_0.set_attenuation(0, 10.0)
        if False:
            self.iio_fmcomms2_sink_0.set_attenuation(1, 10.0)
        self.iio_fmcomms2_sink_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_file_sink_0_1 = blocks.file_sink(gr.sizeof_gr_complex*1, Rx1_path, False)
        self.blocks_file_sink_0_1.set_unbuffered(False)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_gr_complex*1, Rx2_path, False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, baseband, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.iio_fmcomms2_sink_0, 0))
        self.connect((self.iio_fmcomms2_source_0, 0), (self.low_pass_filter_0_0, 0))
        self.connect((self.iio_fmcomms2_source_0, 1), (self.low_pass_filter_1, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.blocks_file_sink_0_1, 0))
        self.connect((self.low_pass_filter_1, 0), (self.blocks_file_sink_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "local_SP_PhaseSync")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.iio_fmcomms2_sink_0.set_samplerate(self.samp_rate)
        self.iio_fmcomms2_source_0.set_samplerate(self.samp_rate)
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, 5000, 2000, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.samp_rate, 5000, 2000, window.WIN_HAMMING, 6.76))

    def get_pluto1(self):
        return self.pluto1

    def set_pluto1(self, pluto1):
        self.pluto1 = pluto1

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.iio_fmcomms2_sink_0.set_frequency(self.freq)
        self.iio_fmcomms2_source_0.set_frequency(self.freq)

    def get_baseband(self):
        return self.baseband

    def set_baseband(self, baseband):
        self.baseband = baseband
        self.analog_sig_source_x_0.set_frequency(self.baseband)

    def get_Tx1_path(self):
        return self.Tx1_path

    def set_Tx1_path(self, Tx1_path):
        self.Tx1_path = Tx1_path

    def get_Rx2_path(self):
        return self.Rx2_path

    def set_Rx2_path(self, Rx2_path):
        self.Rx2_path = Rx2_path
        self.blocks_file_sink_0_0.open(self.Rx2_path)

    def get_Rx1_path(self):
        return self.Rx1_path

    def set_Rx1_path(self, Rx1_path):
        self.Rx1_path = Rx1_path
        self.blocks_file_sink_0_1.open(self.Rx1_path)




def main(top_block_cls=local_SP_PhaseSync, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
