from gnuradio import gr
import struct
import numpy as np

NUM_CHANNELS = 16
SAMPLES_PER_PACKET = 21
PACKET_HEADER_SIZE = 88
EXPECTED_PACKET_SIZE = 1432
MAX_PACKETS_PER_WORK = 10

class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='CIAA UDP Unpacker',
            in_sig=[np.uint8],
            out_sig=[np.float32]*NUM_CHANNELS
        )
        self.buffer = bytearray()
        self.packet_count = 0
        self.error_count = 0
        self.set_output_multiple(SAMPLES_PER_PACKET)
    
    def work(self, input_items, output_items):
        in_len = len(input_items[0])
        self.buffer.extend(input_items[0].tobytes())
        
        n_produced = 0
        max_output = len(output_items[0])
        packets_processed = 0

        while (len(self.buffer) >= EXPECTED_PACKET_SIZE and 
               n_produced + SAMPLES_PER_PACKET <= max_output and
               packets_processed < MAX_PACKETS_PER_WORK):
            
            data = self.buffer[:EXPECTED_PACKET_SIZE]
            self.buffer = self.buffer[EXPECTED_PACKET_SIZE:]
            self.packet_count += 1
            packets_processed += 1

            try:
                payload_start = PACKET_HEADER_SIZE
                
                for row in range(SAMPLES_PER_PACKET):
                    for ch in range(NUM_CHANNELS):
                        offset = payload_start + (row * NUM_CHANNELS * 4) + (ch * 4)
                        
                        if offset + 4 <= len(data):
                            word32 = struct.unpack('<I', data[offset:offset+4])[0]
                            value16 = word32 & 0xFFFF
                            signed_val = struct.unpack('<h', struct.pack('<H', value16))[0]
                            output_items[ch][n_produced] = float(signed_val)
                    
                    n_produced += 1
                
            except Exception as e:
                self.error_count += 1
                if self.error_count <= 10:
                    print(f"ERROR paquete #{self.packet_count}: {e}")

        if self.packet_count % 100 == 0 and self.packet_count > 0:
            print(f"Paquete {self.packet_count}: {packets_processed} procesados, buffer: {len(self.buffer)} bytes")

        self.consume_each(in_len)
        return n_produced
    
    def stop(self):
        print(f"\n=== ESTADÍSTICAS FINALES ===")
        print(f"Paquetes procesados: {self.packet_count}")
        print(f"Errores: {self.error_count}")
        print(f"Tasa error: {100*self.error_count/max(1, self.packet_count):.2f}%")
        return True
