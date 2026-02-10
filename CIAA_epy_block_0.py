import numpy as np
from gnuradio import gr
import sys
sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf')
sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf\gnuradio')
import ciaa_control

class blk(gr.basic_block):
    """Maneja clicks de botones CIAA"""
    def __init__(self, reset_btn=0, enable_btn=0):
        gr.basic_block.__init__(
            self,
            name='CIAA Button Handler',
            in_sig=None,
            out_sig=None
        )
        self.ctrl = ciaa_control.get_controller()
        self.reset_btn = reset_btn
        self.enable_btn = enable_btn
        print("[OK] CIAA Button Handler inicializado")
    
    def handle_reset(self):
        """Ejecuta RESET"""
        print("\n[RESET] System pressed")
        if self.ctrl and self.ctrl.connected:
            self.ctrl.reset_system()
            self.ctrl.reset_fifo()
        else:
            print("[OFFLINE] RESET command")
    
    def handle_enable(self):
        """Ejecuta ENABLE"""
        print("\n[ENABLE] Acquisition pressed")
        if self.ctrl and self.ctrl.connected:
            self.ctrl.enable_system(True)
        else:
            print("[OFFLINE] ENABLE command")