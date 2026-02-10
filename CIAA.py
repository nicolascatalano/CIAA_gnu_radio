#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: nix
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import network
from gnuradio import pdu
import CIAA_epy_block_0 as epy_block_0  # embedded python block
import sip
import threading



class CIAA(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "CIAA")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################

        self.qtgui_sink_x_0 = qtgui.sink_f(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.pdu_pdu_to_stream_x_0 = pdu.pdu_to_stream_b(pdu.EARLY_BURST_APPEND, 4096)
        self.network_socket_pdu_0 = network.socket_pdu('UDP_SERVER', '0.0.0.0', '9999', 10000, False)
        self.epy_block_0 = epy_block_0.blk()
        self.blocks_null_sink_0_8 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_7 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_6 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_5 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_4 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_3 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_2_1_2 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_2_1_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_2_1_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_2_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_2_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_2 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_float*1, 'f:\\Proyectos\\sist_adq_dbf\\gnuradio\\sink_channel0', False)
        self.blocks_file_sink_1.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, 'f:\\Proyectos\\sist_adq_dbf\\gnuradio\\sink_UDP', False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.pdu_pdu_to_stream_x_0, 'pdus'))
        self.connect((self.epy_block_0, 0), (self.blocks_file_sink_1, 0))
        self.connect((self.epy_block_0, 1), (self.blocks_null_sink_0, 0))
        self.connect((self.epy_block_0, 2), (self.blocks_null_sink_0_0, 0))
        self.connect((self.epy_block_0, 3), (self.blocks_null_sink_0_1, 0))
        self.connect((self.epy_block_0, 13), (self.blocks_null_sink_0_2, 0))
        self.connect((self.epy_block_0, 14), (self.blocks_null_sink_0_2_0, 0))
        self.connect((self.epy_block_0, 15), (self.blocks_null_sink_0_2_1, 0))
        self.connect((self.epy_block_0, 6), (self.blocks_null_sink_0_2_1_0, 0))
        self.connect((self.epy_block_0, 8), (self.blocks_null_sink_0_2_1_1, 0))
        self.connect((self.epy_block_0, 10), (self.blocks_null_sink_0_2_1_2, 0))
        self.connect((self.epy_block_0, 12), (self.blocks_null_sink_0_3, 0))
        self.connect((self.epy_block_0, 4), (self.blocks_null_sink_0_4, 0))
        self.connect((self.epy_block_0, 5), (self.blocks_null_sink_0_5, 0))
        self.connect((self.epy_block_0, 7), (self.blocks_null_sink_0_6, 0))
        self.connect((self.epy_block_0, 9), (self.blocks_null_sink_0_7, 0))
        self.connect((self.epy_block_0, 11), (self.blocks_null_sink_0_8, 0))
        self.connect((self.epy_block_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.pdu_pdu_to_stream_x_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.pdu_pdu_to_stream_x_0, 0), (self.epy_block_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "CIAA")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)




def main(top_block_cls=CIAA, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

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
