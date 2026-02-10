#!/usr/bin/env python3
"""
CIAA Control Module para GNU Radio
Maneja la comunicación SSH y configuración de registros FPGA
"""

import sys
import os
sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf')

try:
    import sshClient
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False
    print("WARNING: sshClient not available - CIAA control disabled")

# Direcciones base de memoria
DATA_BASE_ADDR = 0x43C00000
PREPROC_BASE_ADDR = 0x43C30000

# Registros de control
RESET_ASYNC = DATA_BASE_ADDR + 0x004
FIFORST = DATA_BASE_ADDR + 0x008
ENABLE = DATA_BASE_ADDR + 0x010
DEBUG_Control_base = DATA_BASE_ADDR + 0x080
FIFOFLAGSRST = DATA_BASE_ADDR + 0x180

# Registros de preprocesamiento
FIFO_Input_Mux_Control = PREPROC_BASE_ADDR + 0x04
DATA_Source_Mux_Control = PREPROC_BASE_ADDR + 0x08

# Modos de DEBUG_Control_base
DEBUG_MODES = {
    'DISABLED': 0x0,
    'CONT_NBITS': 0xF,  # Contador
    'MIDSCALE_SH': 0x1,
    'DESERIALIZER': 0xD
}

# FIFO_Input_Mux_Control
FIFO_MUX_OPTIONS = {
    'NONE': 0,
    'PREPROC_DATA': 1,
    'COUNTER_POST_PROC': 2,
    'RAW_DATA': 3,
    'MUX_DATA': 4,
    'BAND_MIXER': 5,
    'BAND_FILTER': 6,
    'CH_MIXER': 7
}

# DATA_Source_Mux_Control
DATA_SOURCE_OPTIONS = {
    'DATOS_ADC': 0,
    'OSC_LOC': 1,
    'CONTADOR': 2
}

class CIAAController:
    """Controlador SSH para CIAA-ACC"""
    
    def __init__(self):
        self.ssh = None
        self.connected = False
        if SSH_AVAILABLE:
            try:
                self.ssh = sshClient.ShellHandler()
                self.connected = self.ssh.isConnected
                if self.connected:
                    print("OK CIAA conectado (192.168.0.22)")
            except Exception as e:
                print(f"Error conectando a CIAA: {e}")
                self.connected = False
    
    def write_register(self, addr, value):
        """Escribe un registro via AXI-Lite"""
        if not self.connected:
            print(f"[OFFLINE] Write 0x{addr:08x} = 0x{value:08x}")
            return False
        
        try:
            cmd = f'/mnt/currentVersions/./axi_rw_test.elf w {addr:x} {value:x}'
            result = self.ssh.execute(cmd)
            print(f"OK Write 0x{addr:08x} = 0x{value:08x}")
            return True
        except Exception as e:
            print(f"Error escribiendo registro: {e}")
            return False
    
    def reset_system(self):
        """Reset asíncrono del sistema"""
        print("=== RESET ASYNC ===")
        return self.write_register(RESET_ASYNC, 10)
    
    def reset_fifo(self):
        """Reset del FIFO de datos"""
        print("=== RESET FIFO ===")
        return self.write_register(FIFORST, 1)
    
    def enable_system(self, enable=True):
        """Habilita/deshabilita el sistema"""
        val = 1 if enable else 0
        print(f"=== {'ENABLE' if enable else 'DISABLE'} ===")
        return self.write_register(ENABLE, val)
    
    def set_debug_mode(self, mode_value):
        """Configura modo de debug (recibe valor directamente)"""
        print(f"=== DEBUG MODE: 0x{mode_value:X} ===")
        return self.write_register(DEBUG_Control_base, mode_value)
    
    def set_fifo_input_mux(self, mux_value):
        """Configura entrada del FIFO (recibe valor directamente)"""
        print(f"=== FIFO INPUT MUX: {mux_value} ===")
        return self.write_register(FIFO_Input_Mux_Control, mux_value)
    
    def set_data_source_mux(self, source_value):
        """Configura fuente de datos (recibe valor directamente)"""
        print(f"=== DATA SOURCE MUX: {source_value} ===")
        return self.write_register(DATA_Source_Mux_Control, source_value)
    
    def configure_preset(self, preset_name):
        """Aplica configuración predefinida"""
        if preset_name == "Counter Test":
            self.reset_system()
            self.reset_fifo()
            self.set_debug_mode(0xF)  # CONT_NBITS
            self.set_data_source_mux(2)  # CONTADOR
            self.set_fifo_input_mux(4)  # MUX_DATA
            self.enable_system(True)
        elif preset_name == "ADC Raw":
            self.reset_system()
            self.reset_fifo()
            self.set_debug_mode(0x0)  # DISABLED
            self.set_data_source_mux(0)  # DATOS_ADC
            self.set_fifo_input_mux(3)  # RAW_DATA
            self.enable_system(True)
        elif preset_name == "Preprocessed":
            self.reset_system()
            self.reset_fifo()
            self.set_debug_mode(0x0)  # DISABLED
            self.set_data_source_mux(0)  # DATOS_ADC
            self.set_fifo_input_mux(1)  # PREPROC_DATA
            self.enable_system(True)
        
        print(f"OK Configuración '{preset_name}' aplicada\n")

# Instancia global
_ciaa_controller = None

def get_controller():
    """Obtiene la instancia global del controlador"""
    global _ciaa_controller
    if _ciaa_controller is None:
        _ciaa_controller = CIAAController()
    return _ciaa_controller