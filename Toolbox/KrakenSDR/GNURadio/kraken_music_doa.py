#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.3.0

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import krakensdr



from gnuradio import qtgui

class kraken_music_doa(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
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

        self.settings = Qt.QSettings("GNU Radio", "kraken_music_doa")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2400000
        self.freq = freq = 433.000
        self.decimation = decimation = 128
        self.cpi_size = cpi_size = 2**20

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            360, #size
            1000, #samp_rate
            'DOA Graph', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            (samp_rate//decimation), #bw
            'CH_0 Decimated FFT', #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.1)
        self.qtgui_freq_sink_x_0.set_y_axis((-60), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.krakensdr_krakensdr_source_0 = krakensdr.krakensdr_source('127.0.0.1', 5000, 5001, 5, freq, [40.2, 40.2, 40.2, 40.2, 40.2], False)
        self.krakensdr_doa_music_0 = krakensdr.doa_music((cpi_size//decimation), freq, 0.26, 5, 'UCA')
        self.fir_filter_xxx_0_0_2 = filter.fir_filter_ccc(decimation, [decimation*5])
        self.fir_filter_xxx_0_0_2.declare_sample_delay(0)
        self.fir_filter_xxx_0_0_1 = filter.fir_filter_ccc(decimation, [decimation*5])
        self.fir_filter_xxx_0_0_1.declare_sample_delay(0)
        self.fir_filter_xxx_0_0_0 = filter.fir_filter_ccc(decimation, [decimation*5])
        self.fir_filter_xxx_0_0_0.declare_sample_delay(0)
        self.fir_filter_xxx_0_0 = filter.fir_filter_ccc(decimation, [decimation*5])
        self.fir_filter_xxx_0_0.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_ccc(decimation, [decimation*5])
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.blocks_vector_to_stream_0_2_0 = blocks.vector_to_stream(gr.sizeof_float*1, 360)
        self.blocks_stream_to_vector_0_0_2 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (cpi_size//decimation))
        self.blocks_stream_to_vector_0_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (cpi_size//decimation))
        self.blocks_stream_to_vector_0_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (cpi_size//decimation))
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (cpi_size//decimation))
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (cpi_size//decimation))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_stream_to_vector_0, 0), (self.krakensdr_doa_music_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.krakensdr_doa_music_0, 1))
        self.connect((self.blocks_stream_to_vector_0_0_0, 0), (self.krakensdr_doa_music_0, 2))
        self.connect((self.blocks_stream_to_vector_0_0_1, 0), (self.krakensdr_doa_music_0, 3))
        self.connect((self.blocks_stream_to_vector_0_0_2, 0), (self.krakensdr_doa_music_0, 4))
        self.connect((self.blocks_vector_to_stream_0_2_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.fir_filter_xxx_0_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.fir_filter_xxx_0_0_0, 0), (self.blocks_stream_to_vector_0_0_0, 0))
        self.connect((self.fir_filter_xxx_0_0_1, 0), (self.blocks_stream_to_vector_0_0_1, 0))
        self.connect((self.fir_filter_xxx_0_0_2, 0), (self.blocks_stream_to_vector_0_0_2, 0))
        self.connect((self.krakensdr_doa_music_0, 0), (self.blocks_vector_to_stream_0_2_0, 0))
        self.connect((self.krakensdr_krakensdr_source_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.krakensdr_krakensdr_source_0, 1), (self.fir_filter_xxx_0_0, 0))
        self.connect((self.krakensdr_krakensdr_source_0, 2), (self.fir_filter_xxx_0_0_0, 0))
        self.connect((self.krakensdr_krakensdr_source_0, 3), (self.fir_filter_xxx_0_0_1, 0))
        self.connect((self.krakensdr_krakensdr_source_0, 4), (self.fir_filter_xxx_0_0_2, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "kraken_music_doa")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(0, (self.samp_rate//self.decimation))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.krakensdr_krakensdr_source_0.set_freq(self.freq)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.fir_filter_xxx_0.set_taps([self.decimation*5])
        self.fir_filter_xxx_0_0.set_taps([self.decimation*5])
        self.fir_filter_xxx_0_0_0.set_taps([self.decimation*5])
        self.fir_filter_xxx_0_0_1.set_taps([self.decimation*5])
        self.fir_filter_xxx_0_0_2.set_taps([self.decimation*5])
        self.qtgui_freq_sink_x_0.set_frequency_range(0, (self.samp_rate//self.decimation))

    def get_cpi_size(self):
        return self.cpi_size

    def set_cpi_size(self, cpi_size):
        self.cpi_size = cpi_size




def main(top_block_cls=kraken_music_doa, options=None):

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
