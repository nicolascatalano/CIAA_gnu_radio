import sys
sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf')
sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf\gnuradio')

import numpy as np
from gnuradio import gr
import ciaa_control

class blk(gr.sync_block):
    """Maneja clicks de botones CIAA"""
    def __init__(self, reset_btn=0, enable_btn=0):
        gr.sync_block.__init__(
            self,
            name='CIAA Button Handler',
            in_sig=None,
            out_sig=None
        )
        self.ctrl = ciaa_control.get_controller()
        self.reset_btn = reset_btn
        self.enable_btn = enable_btn
        self.last_reset = 0
        self.last_enable = 0
    
    def set_reset(self, val):
        """Callback para botón RESET"""
        if val == 1 and self.last_reset == 0:  # Flanco ascendente
            print("\n🔄 RESET System pressed")
            if self.ctrl:
                self.ctrl.reset_system()
                self.ctrl.reset_fifo()
        self.last_reset = val
    
    def set_enable(self, val):
        """Callback para botón ENABLE"""
        if val == 1 and self.last_enable == 0:  # Flanco ascendente
            print("\n▶ ENABLE Acquisition pressed")
            if self.ctrl:
                self.ctrl.enable_system(True)
        self.last_enable = val
    
    def work(self, input_items, output_items):
        # Monitorear cambios en botones
        if hasattr(self, 'reset_btn') and self.reset_btn != self.last_reset:
            self.set_reset(self.reset_btn)
        
        if hasattr(self, 'enable_btn') and self.enable_btn != self.last_enable:
            self.set_enable(self.enable_btn)
        
        return 0