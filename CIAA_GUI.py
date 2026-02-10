#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: CIAA Control GUI
# Author: CIAA Project
# Description: Interfaz gráfica para control CIAA-ACC con visualización de flujo de datos
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5.QtCore import QObject, pyqtSlot
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
import CIAA_GUI_epy_block_0 as epy_block_0  # embedded python block
import CIAA_GUI_epy_block_ciaa_apply as epy_block_ciaa_apply  # embedded python block
import CIAA_GUI_epy_block_unpacker as epy_block_unpacker  # embedded python block
import sip
import sys; sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf\gnuradio'); sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf'); import ciaa_control
import threading



class CIAA_GUI(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "CIAA Control GUI", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("CIAA Control GUI")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "CIAA_GUI")

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
        self.variable_qtgui_push_button_1 = variable_qtgui_push_button_1 = 0
        self.variable_qtgui_push_button_0 = variable_qtgui_push_button_0 = 0
        self.samp_rate = samp_rate = 65000000
        self.fifo_input_mux = fifo_input_mux = 3
        self.debug_mode = debug_mode = 0
        self.data_source_mux = data_source_mux = 0

        ##################################################
        # Blocks
        ##################################################

        _variable_qtgui_push_button_1_push_button = Qt.QPushButton('ENABLE Acquisition')
        _variable_qtgui_push_button_1_push_button = Qt.QPushButton('ENABLE Acquisition')
        self._variable_qtgui_push_button_1_choices = {'Pressed': 1, 'Released': 0}
        _variable_qtgui_push_button_1_push_button.pressed.connect(lambda: self.set_variable_qtgui_push_button_1(self._variable_qtgui_push_button_1_choices['Pressed']))
        _variable_qtgui_push_button_1_push_button.released.connect(lambda: self.set_variable_qtgui_push_button_1(self._variable_qtgui_push_button_1_choices['Released']))
        self.top_layout.addWidget(_variable_qtgui_push_button_1_push_button)
        _variable_qtgui_push_button_0_push_button = Qt.QPushButton('RESET System')
        _variable_qtgui_push_button_0_push_button = Qt.QPushButton('RESET System')
        self._variable_qtgui_push_button_0_choices = {'Pressed': 1, 'Released': 0}
        _variable_qtgui_push_button_0_push_button.pressed.connect(lambda: self.set_variable_qtgui_push_button_0(self._variable_qtgui_push_button_0_choices['Pressed']))
        _variable_qtgui_push_button_0_push_button.released.connect(lambda: self.set_variable_qtgui_push_button_0(self._variable_qtgui_push_button_0_choices['Released']))
        self.top_layout.addWidget(_variable_qtgui_push_button_0_push_button)
        # Create the options list
        self._fifo_input_mux_options = [0, 1, 2, 3, 4]
        # Create the labels list
        self._fifo_input_mux_labels = ['NONE', 'PREPROC_DATA', 'COUNTER_POST_PROC', 'RAW_DATA', 'MUX_DATA']
        # Create the combo box
        # Create the radio buttons
        self._fifo_input_mux_group_box = Qt.QGroupBox("FIFO Input" + ": ")
        self._fifo_input_mux_box = Qt.QVBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._fifo_input_mux_button_group = variable_chooser_button_group()
        self._fifo_input_mux_group_box.setLayout(self._fifo_input_mux_box)
        for i, _label in enumerate(self._fifo_input_mux_labels):
            radio_button = Qt.QRadioButton(_label)
            self._fifo_input_mux_box.addWidget(radio_button)
            self._fifo_input_mux_button_group.addButton(radio_button, i)
        self._fifo_input_mux_callback = lambda i: Qt.QMetaObject.invokeMethod(self._fifo_input_mux_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._fifo_input_mux_options.index(i)))
        self._fifo_input_mux_callback(self.fifo_input_mux)
        self._fifo_input_mux_button_group.buttonClicked[int].connect(
            lambda i: self.set_fifo_input_mux(self._fifo_input_mux_options[i]))
        self.top_grid_layout.addWidget(self._fifo_input_mux_group_box, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._debug_mode_options = [0, 15, 1, 13]
        # Create the labels list
        self._debug_mode_labels = ['DISABLED (ADC)', 'CONT_NBITS (Counter)', 'MIDSCALE_SH', 'DESERIALIZER']
        # Create the combo box
        # Create the radio buttons
        self._debug_mode_group_box = Qt.QGroupBox("Debug Mode" + ": ")
        self._debug_mode_box = Qt.QVBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._debug_mode_button_group = variable_chooser_button_group()
        self._debug_mode_group_box.setLayout(self._debug_mode_box)
        for i, _label in enumerate(self._debug_mode_labels):
            radio_button = Qt.QRadioButton(_label)
            self._debug_mode_box.addWidget(radio_button)
            self._debug_mode_button_group.addButton(radio_button, i)
        self._debug_mode_callback = lambda i: Qt.QMetaObject.invokeMethod(self._debug_mode_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._debug_mode_options.index(i)))
        self._debug_mode_callback(self.debug_mode)
        self._debug_mode_button_group.buttonClicked[int].connect(
            lambda i: self.set_debug_mode(self._debug_mode_options[i]))
        self.top_grid_layout.addWidget(self._debug_mode_group_box, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._data_source_mux_options = [0, 1, 2]
        # Create the labels list
        self._data_source_mux_labels = ['DATOS_ADC', 'OSC_LOC', 'CONTADOR']
        # Create the combo box
        # Create the radio buttons
        self._data_source_mux_group_box = Qt.QGroupBox("Data Source" + ": ")
        self._data_source_mux_box = Qt.QVBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._data_source_mux_button_group = variable_chooser_button_group()
        self._data_source_mux_group_box.setLayout(self._data_source_mux_box)
        for i, _label in enumerate(self._data_source_mux_labels):
            radio_button = Qt.QRadioButton(_label)
            self._data_source_mux_box.addWidget(radio_button)
            self._data_source_mux_button_group.addButton(radio_button, i)
        self._data_source_mux_callback = lambda i: Qt.QMetaObject.invokeMethod(self._data_source_mux_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._data_source_mux_options.index(i)))
        self._data_source_mux_callback(self.data_source_mux)
        self._data_source_mux_button_group.buttonClicked[int].connect(
            lambda i: self.set_data_source_mux(self._data_source_mux_options[i]))
        self.top_grid_layout.addWidget(self._data_source_mux_group_box, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            1024, #size
            samp_rate, #samp_rate
            "CIAA Channels 0-3", #name
            4, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-20000, 20000)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Ch0', 'Ch1', 'Ch2', 'Ch3', 'Ch4',
            'Ch5', 'Ch6', 'Ch7', 'Ch8', 'Ch9']
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
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 4, 0, 4, 4)
        for r in range(4, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "CIAA Spectrum", #name
            4,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_0.set_plot_pos_half(not True)

        labels = ['Ch0', 'Ch1', 'Ch2', 'Ch3', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(4):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 8, 0, 4, 4)
        for r in range(8, 12):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pdu_pdu_to_stream_x_0 = pdu.pdu_to_stream_b(pdu.EARLY_BURST_APPEND, 512)
        self.network_socket_pdu_0 = network.socket_pdu('UDP_SERVER', '0.0.0.0', '9999', 10000, False)
        self.epy_block_unpacker = epy_block_unpacker.blk()
        self.epy_block_ciaa_apply = epy_block_ciaa_apply.blk(debug_mode=debug_mode, data_source=data_source_mux, fifo_input=fifo_input_mux)
        self.epy_block_0 = epy_block_0.blk(reset_btn=variable_qtgui_push_button_0, enable_btn=variable_qtgui_push_button_1)
        self.blocks_null_sink_0_9 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_8 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_7 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_6 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_5 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_4 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_3 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_2 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_10 = blocks.null_sink(gr.sizeof_float*1)
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
        self.connect((self.epy_block_unpacker, 0), (self.blocks_file_sink_1, 0))
        self.connect((self.epy_block_unpacker, 5), (self.blocks_null_sink_0, 0))
        self.connect((self.epy_block_unpacker, 10), (self.blocks_null_sink_0_0, 0))
        self.connect((self.epy_block_unpacker, 11), (self.blocks_null_sink_0_1, 0))
        self.connect((self.epy_block_unpacker, 6), (self.blocks_null_sink_0_10, 0))
        self.connect((self.epy_block_unpacker, 12), (self.blocks_null_sink_0_2, 0))
        self.connect((self.epy_block_unpacker, 15), (self.blocks_null_sink_0_3, 0))
        self.connect((self.epy_block_unpacker, 9), (self.blocks_null_sink_0_4, 0))
        self.connect((self.epy_block_unpacker, 8), (self.blocks_null_sink_0_5, 0))
        self.connect((self.epy_block_unpacker, 7), (self.blocks_null_sink_0_6, 0))
        self.connect((self.epy_block_unpacker, 14), (self.blocks_null_sink_0_7, 0))
        self.connect((self.epy_block_unpacker, 4), (self.blocks_null_sink_0_8, 0))
        self.connect((self.epy_block_unpacker, 13), (self.blocks_null_sink_0_9, 0))
        self.connect((self.epy_block_unpacker, 1), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.epy_block_unpacker, 3), (self.qtgui_freq_sink_x_0, 3))
        self.connect((self.epy_block_unpacker, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.epy_block_unpacker, 2), (self.qtgui_freq_sink_x_0, 2))
        self.connect((self.epy_block_unpacker, 2), (self.qtgui_time_sink_x_0, 2))
        self.connect((self.epy_block_unpacker, 3), (self.qtgui_time_sink_x_0, 3))
        self.connect((self.epy_block_unpacker, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.epy_block_unpacker, 1), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.pdu_pdu_to_stream_x_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.pdu_pdu_to_stream_x_0, 0), (self.epy_block_unpacker, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "CIAA_GUI")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_variable_qtgui_push_button_1(self):
        return self.variable_qtgui_push_button_1

    def set_variable_qtgui_push_button_1(self, variable_qtgui_push_button_1):
        self.variable_qtgui_push_button_1 = variable_qtgui_push_button_1
        self.epy_block_0.enable_btn = self.variable_qtgui_push_button_1

    def get_variable_qtgui_push_button_0(self):
        return self.variable_qtgui_push_button_0

    def set_variable_qtgui_push_button_0(self, variable_qtgui_push_button_0):
        self.variable_qtgui_push_button_0 = variable_qtgui_push_button_0
        self.epy_block_0.reset_btn = self.variable_qtgui_push_button_0

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_fifo_input_mux(self):
        return self.fifo_input_mux

    def set_fifo_input_mux(self, fifo_input_mux):
        self.fifo_input_mux = fifo_input_mux
        self._fifo_input_mux_callback(self.fifo_input_mux)

    def get_debug_mode(self):
        return self.debug_mode

    def set_debug_mode(self, debug_mode):
        self.debug_mode = debug_mode
        self._debug_mode_callback(self.debug_mode)

    def get_data_source_mux(self):
        return self.data_source_mux

    def set_data_source_mux(self, data_source_mux):
        self.data_source_mux = data_source_mux
        self._data_source_mux_callback(self.data_source_mux)




def main(top_block_cls=CIAA_GUI, options=None):

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
