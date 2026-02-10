#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: CIAA UDP Receiver
# Author: CIAA Project
# Description: UDP receiver for CIAA-ACC data acquisition with packet unpacker
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
import CIAA_UDP_Receiver_Working_epy_block_ciaa_unpacker as epy_block_ciaa_unpacker  # embedded python block
import sip
import threading



class CIAA_UDP_Receiver_Working(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "CIAA UDP Receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("CIAA UDP Receiver")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "CIAA_UDP_Receiver_Working")

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
        self.clk_divider = clk_divider = 0
        self.udp_port = udp_port = 9999
        self.samp_rate = samp_rate = 65e6 / (clk_divider + 1)

        ##################################################
        # Blocks
        ##################################################

        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            105, #size
            samp_rate, #samp_rate
            "CIAA Channels 0-3 (Time)", #name
            4, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-20000, 20000)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Ch0', 'Ch1', 'Ch2', 'Ch3', '',
            '', '', '', '', '']
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


        for i in range(4):
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
        self.network_socket_pdu_0 = network.socket_pdu('UDP_SERVER', '0.0.0.0', str(udp_port), 10000, False)
        self.epy_block_ciaa_unpacker = epy_block_ciaa_unpacker.blk(data_type='int16', warn_overflow=True)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_head_0 = blocks.head(gr.sizeof_float*1, 105)
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_float*1, 'ciaa_ch0_5packets.dat', False)
        self.blocks_file_sink_1.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.epy_block_ciaa_unpacker, 'pdus'))
        self.connect((self.blocks_head_0, 0), (self.blocks_file_sink_1, 0))
        self.connect((self.epy_block_ciaa_unpacker, 0), (self.blocks_head_0, 0))
        self.connect((self.epy_block_ciaa_unpacker, 15), (self.blocks_null_sink_0, 11))
        self.connect((self.epy_block_ciaa_unpacker, 7), (self.blocks_null_sink_0, 3))
        self.connect((self.epy_block_ciaa_unpacker, 4), (self.blocks_null_sink_0, 0))
        self.connect((self.epy_block_ciaa_unpacker, 9), (self.blocks_null_sink_0, 5))
        self.connect((self.epy_block_ciaa_unpacker, 13), (self.blocks_null_sink_0, 9))
        self.connect((self.epy_block_ciaa_unpacker, 10), (self.blocks_null_sink_0, 6))
        self.connect((self.epy_block_ciaa_unpacker, 5), (self.blocks_null_sink_0, 1))
        self.connect((self.epy_block_ciaa_unpacker, 6), (self.blocks_null_sink_0, 2))
        self.connect((self.epy_block_ciaa_unpacker, 14), (self.blocks_null_sink_0, 10))
        self.connect((self.epy_block_ciaa_unpacker, 8), (self.blocks_null_sink_0, 4))
        self.connect((self.epy_block_ciaa_unpacker, 11), (self.blocks_null_sink_0, 7))
        self.connect((self.epy_block_ciaa_unpacker, 12), (self.blocks_null_sink_0, 8))
        self.connect((self.epy_block_ciaa_unpacker, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.epy_block_ciaa_unpacker, 2), (self.qtgui_time_sink_x_0, 2))
        self.connect((self.epy_block_ciaa_unpacker, 3), (self.qtgui_time_sink_x_0, 3))
        self.connect((self.epy_block_ciaa_unpacker, 1), (self.qtgui_time_sink_x_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "CIAA_UDP_Receiver_Working")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_clk_divider(self):
        return self.clk_divider

    def set_clk_divider(self, clk_divider):
        self.clk_divider = clk_divider
        self.set_samp_rate(65e6 / (self.clk_divider + 1))

    def get_udp_port(self):
        return self.udp_port

    def set_udp_port(self, udp_port):
        self.udp_port = udp_port

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)




def main(top_block_cls=CIAA_UDP_Receiver_Working, options=None):

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
