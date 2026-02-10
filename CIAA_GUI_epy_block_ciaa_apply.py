import numpy as np
from gnuradio import gr
import sys
sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf')
sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf\gnuradio')
import ciaa_control

class blk(gr.basic_block):
    """Aplica configuración CIAA"""
    def __init__(self, debug_mode=0, data_source=0, fifo_input=0):
        gr.basic_block.__init__(
            self,
            name='CIAA Config Apply',
            in_sig=None,
            out_sig=None
        )
        self.ctrl = ciaa_control.get_controller()
        self.last_debug = -1
        self.last_source = -1
        self.last_fifo = -1
        print("OK CIAA Config Apply inicializado")
    
    def set_debug_mode(self, val):
        if self.ctrl and self.last_debug != val:
            self.ctrl.set_debug_mode(val)
            self.last_debug = val
    
    def set_data_source(self, val):
        if self.ctrl and self.last_source != val:
            self.ctrl.set_data_source_mux(val)
            self.last_source = val
    
    def set_fifo_input(self, val):
        if self.ctrl and self.last_fifo != val:
            self.ctrl.set_fifo_input_mux(val)
            self.last_fifo = val