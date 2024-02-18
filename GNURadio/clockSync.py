#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Clock Sync
# GNU Radio version: 3.10.1.1

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
from gnuradio import analog
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio



from gnuradio import qtgui

class clockSync(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Clock Sync", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Clock Sync")
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

        self.settings = Qt.QSettings("GNU Radio", "clockSync")

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
        self.samp_rate = samp_rate = 3200000
        self.freq = freq = 100000000
        self.baseband = baseband = 500

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_time_sink_x_0_0_0 = qtgui.time_sink_c(
            1024, #size
            samp_rate, #samp_rate
            "", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0.set_y_axis(-1.5, 1.5)

        self.qtgui_time_sink_x_0_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_0.enable_stem_plot(False)


        labels = ['Pluto 2.1 WHITE', 'Pluto 1.1 BLACK', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 0, 0, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 0, 0, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(4):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Plutos", #name
            2,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-180, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ["Pluto 2.1 WHITE", "Pluto1.1 BLACK", '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.low_pass_filter_0_1_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                5000,
                2000,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0_1 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                5000,
                2000,
                window.WIN_HAMMING,
                6.76))
        self.iio_pluto_sink_0_0_0 = iio.fmcomms2_sink_fc32('ip:192.168.1.1' if 'ip:192.168.1.1' else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0_0_0.set_len_tag_key('')
        self.iio_pluto_sink_0_0_0.set_bandwidth(20000000)
        self.iio_pluto_sink_0_0_0.set_frequency(freq)
        self.iio_pluto_sink_0_0_0.set_samplerate(samp_rate)
        self.iio_pluto_sink_0_0_0.set_attenuation(0, 0.0)
        self.iio_pluto_sink_0_0_0.set_filter_params('Auto', '', 0, 0)
        self.iio_pluto_sink_0_0 = iio.fmcomms2_sink_fc32('ip:192.168.2.1' if 'ip:192.168.2.1' else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0_0.set_len_tag_key('')
        self.iio_pluto_sink_0_0.set_bandwidth(20000000)
        self.iio_pluto_sink_0_0.set_frequency(freq)
        self.iio_pluto_sink_0_0.set_samplerate(samp_rate)
        self.iio_pluto_sink_0_0.set_attenuation(0, 0.0)
        self.iio_pluto_sink_0_0.set_filter_params('Auto', '', 0, 0)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, baseband, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0_0, 0), (self.low_pass_filter_0_1, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.low_pass_filter_0_1_0, 0))
        self.connect((self.low_pass_filter_0_1, 0), (self.iio_pluto_sink_0_0, 0))
        self.connect((self.low_pass_filter_0_1, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.low_pass_filter_0_1, 0), (self.qtgui_time_sink_x_0_0_0, 0))
        self.connect((self.low_pass_filter_0_1_0, 0), (self.iio_pluto_sink_0_0_0, 0))
        self.connect((self.low_pass_filter_0_1_0, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.low_pass_filter_0_1_0, 0), (self.qtgui_time_sink_x_0_0_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "clockSync")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.iio_pluto_sink_0_0.set_samplerate(self.samp_rate)
        self.iio_pluto_sink_0_0_0.set_samplerate(self.samp_rate)
        self.low_pass_filter_0_1.set_taps(firdes.low_pass(1, self.samp_rate, 5000, 2000, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_1_0.set_taps(firdes.low_pass(1, self.samp_rate, 5000, 2000, window.WIN_HAMMING, 6.76))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0_0_0.set_samp_rate(self.samp_rate)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.iio_pluto_sink_0_0.set_frequency(self.freq)
        self.iio_pluto_sink_0_0_0.set_frequency(self.freq)

    def get_baseband(self):
        return self.baseband

    def set_baseband(self, baseband):
        self.baseband = baseband
        self.analog_sig_source_x_0_0.set_frequency(self.baseband)




def main(top_block_cls=clockSync, options=None):

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
