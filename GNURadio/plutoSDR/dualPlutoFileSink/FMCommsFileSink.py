#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: FMComms File Sink
# GNU Radio version: 3.10.7.0

from packaging.version import Version as StrictVersion
from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio



class FMCommsFileSink(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "FMComms File Sink", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("FMComms File Sink")
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

        self.settings = Qt.QSettings("GNU Radio", "FMCommsFileSink")

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
        self.samp_rate = samp_rate = 2600000
        self.pluto5 = pluto5 = "ip:192.168.5.1"
        self.pluto4 = pluto4 = "ip:192.168.4.1"
        self.pluto3 = pluto3 = "ip:192.168.3.1"
        self.pluto2 = pluto2 = "ip:192.168.2.1"
        self.freq = freq = 915000000
        self.const = const = digital.constellation_bpsk().base()
        self.baseband = baseband = 500
        self.Tx_path = Tx_path = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputTX.iq"
        self.P5_path = P5_path = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP5.iq"
        self.P4_path = P4_path = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP4.iq"
        self.P3_path = P3_path = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP3.iq"
        self.P2_path = P2_path = "/home/sdr/code/sdr-beamforming/GNURadio/plutoSDR/dualPlutoFileSink/fileOutputP2.iq"

        ##################################################
        # Blocks
        ##################################################

        self.iio_fmcomms2_source_0_0_1 = iio.fmcomms2_source_fc32(pluto5, [True, True, True, True], 32768)
        self.iio_fmcomms2_source_0_0_1.set_len_tag_key('packet_len')
        self.iio_fmcomms2_source_0_0_1.set_frequency(freq)
        self.iio_fmcomms2_source_0_0_1.set_samplerate(samp_rate)
        if True:
            self.iio_fmcomms2_source_0_0_1.set_gain_mode(0, 'manual')
            self.iio_fmcomms2_source_0_0_1.set_gain(0, 20)
        if True:
            self.iio_fmcomms2_source_0_0_1.set_gain_mode(1, 'manual')
            self.iio_fmcomms2_source_0_0_1.set_gain(1, 30)
        self.iio_fmcomms2_source_0_0_1.set_quadrature(True)
        self.iio_fmcomms2_source_0_0_1.set_rfdc(True)
        self.iio_fmcomms2_source_0_0_1.set_bbdc(True)
        self.iio_fmcomms2_source_0_0_1.set_filter_params('Auto', '', 0, 0)
        self.iio_fmcomms2_source_0_0 = iio.fmcomms2_source_fc32(pluto2, [True, True, True, True], 32768)
        self.iio_fmcomms2_source_0_0.set_len_tag_key('packet_len')
        self.iio_fmcomms2_source_0_0.set_frequency(freq)
        self.iio_fmcomms2_source_0_0.set_samplerate(samp_rate)
        if True:
            self.iio_fmcomms2_source_0_0.set_gain_mode(0, 'manual')
            self.iio_fmcomms2_source_0_0.set_gain(0, 20)
        if True:
            self.iio_fmcomms2_source_0_0.set_gain_mode(1, 'manual')
            self.iio_fmcomms2_source_0_0.set_gain(1, 16)
        self.iio_fmcomms2_source_0_0.set_quadrature(True)
        self.iio_fmcomms2_source_0_0.set_rfdc(True)
        self.iio_fmcomms2_source_0_0.set_bbdc(True)
        self.iio_fmcomms2_source_0_0.set_filter_params('Auto', '', 0, 0)
        self.iio_fmcomms2_sink_0 = iio.fmcomms2_sink_fc32(pluto4, [True, True, False, False], 4096, False)
        self.iio_fmcomms2_sink_0.set_len_tag_key('')
        self.iio_fmcomms2_sink_0.set_bandwidth(20000000)
        self.iio_fmcomms2_sink_0.set_frequency(freq)
        self.iio_fmcomms2_sink_0.set_samplerate(samp_rate)
        if True:
            self.iio_fmcomms2_sink_0.set_attenuation(0, 12)
        if False:
            self.iio_fmcomms2_sink_0.set_attenuation(1, 10.0)
        self.iio_fmcomms2_sink_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_file_sink_0_4 = blocks.file_sink(gr.sizeof_gr_complex*1, Tx_path, False)
        self.blocks_file_sink_0_4.set_unbuffered(False)
        self.blocks_file_sink_0_3 = blocks.file_sink(gr.sizeof_gr_complex*1, P3_path, False)
        self.blocks_file_sink_0_3.set_unbuffered(False)
        self.blocks_file_sink_0_2_0 = blocks.file_sink(gr.sizeof_gr_complex*1, P5_path, False)
        self.blocks_file_sink_0_2_0.set_unbuffered(False)
        self.blocks_file_sink_0_2 = blocks.file_sink(gr.sizeof_gr_complex*1, P4_path, False)
        self.blocks_file_sink_0_2.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, P2_path, False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, baseband, 2, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_file_sink_0_4, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.iio_fmcomms2_sink_0, 0))
        self.connect((self.iio_fmcomms2_source_0_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.iio_fmcomms2_source_0_0, 1), (self.blocks_file_sink_0_3, 0))
        self.connect((self.iio_fmcomms2_source_0_0_1, 0), (self.blocks_file_sink_0_2, 0))
        self.connect((self.iio_fmcomms2_source_0_0_1, 1), (self.blocks_file_sink_0_2_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "FMCommsFileSink")
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
        self.iio_fmcomms2_source_0_0.set_samplerate(self.samp_rate)
        self.iio_fmcomms2_source_0_0_1.set_samplerate(self.samp_rate)

    def get_pluto5(self):
        return self.pluto5

    def set_pluto5(self, pluto5):
        self.pluto5 = pluto5

    def get_pluto4(self):
        return self.pluto4

    def set_pluto4(self, pluto4):
        self.pluto4 = pluto4

    def get_pluto3(self):
        return self.pluto3

    def set_pluto3(self, pluto3):
        self.pluto3 = pluto3

    def get_pluto2(self):
        return self.pluto2

    def set_pluto2(self, pluto2):
        self.pluto2 = pluto2

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.iio_fmcomms2_sink_0.set_frequency(self.freq)
        self.iio_fmcomms2_source_0_0.set_frequency(self.freq)
        self.iio_fmcomms2_source_0_0_1.set_frequency(self.freq)

    def get_const(self):
        return self.const

    def set_const(self, const):
        self.const = const

    def get_baseband(self):
        return self.baseband

    def set_baseband(self, baseband):
        self.baseband = baseband
        self.analog_sig_source_x_0.set_frequency(self.baseband)

    def get_Tx_path(self):
        return self.Tx_path

    def set_Tx_path(self, Tx_path):
        self.Tx_path = Tx_path
        self.blocks_file_sink_0_4.open(self.Tx_path)

    def get_P5_path(self):
        return self.P5_path

    def set_P5_path(self, P5_path):
        self.P5_path = P5_path
        self.blocks_file_sink_0_2_0.open(self.P5_path)

    def get_P4_path(self):
        return self.P4_path

    def set_P4_path(self, P4_path):
        self.P4_path = P4_path
        self.blocks_file_sink_0_2.open(self.P4_path)

    def get_P3_path(self):
        return self.P3_path

    def set_P3_path(self, P3_path):
        self.P3_path = P3_path
        self.blocks_file_sink_0_3.open(self.P3_path)

    def get_P2_path(self):
        return self.P2_path

    def set_P2_path(self, P2_path):
        self.P2_path = P2_path
        self.blocks_file_sink_0.open(self.P2_path)




def main(top_block_cls=FMCommsFileSink, options=None):

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
