import numpy as np
from gnuradio import gr
import struct
import sys
import pmt
from collections import deque

# ESTRUCTURA REAL: [HEADER(0-87)] [PAYLOAD(88-1431)]
HEADER_OFFSET = 0
PAYLOAD_OFFSET = 88
PAYLOAD_SIZE = 1344
PACKET_SIZE = 1432

try:
    sys.path.insert(0, r'f:\\Proyectos\\sist_adq_dbf\\gnuradio_streaming')
    import packet_parser
    PACKET_PARSER_AVAILABLE = True
except ImportError:
    PACKET_PARSER_AVAILABLE = False

class blk(gr.sync_block):
    """CIAA UDP Packet Unpacker - PDU input, 16 channels output"""
    def __init__(self, data_type='int16', warn_overflow=True):
        print("\n" + "="*70)
        print("CIAA UNPACKER - VERSION 2026-02-09 12:00 - HEADER FIRST")
        print("Header offset: 0 | Payload offset: 88 | Optimized: NumPy | Stats: every 500 pkts")
        print("="*70 + "\n")
        self.data_type = data_type
        self.warn_overflow = warn_overflow
        if PACKET_PARSER_AVAILABLE:
            self.parser = packet_parser.CIAAPacketParser(verbose=False)
        else:
            self.parser = None
        gr.sync_block.__init__(
            self,
            name='CIAA_Unpacker',
            in_sig=None,
            out_sig=[np.float32] * 16,
        )
        self.message_port_register_in(pmt.intern("pdus"))
        self.set_msg_handler(pmt.intern("pdus"), self._handle_pdu)
        self.sample_queue = deque()
        self.current_samples = None
        self.set_output_multiple(21)
        self.packets_received = 0
        self.packets_parsed = 0
        self.saved_packet_count = 0
        self.max_packets_to_save = 10
        self.stop_after_packets = 10
        self.stopped = False

    def _save_packet_analysis(self, packet_bytes, packet_num):
        """Save raw packet, header and payload for analysis"""
        try:
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_dir = r'f:\Proyectos\sist_adq_dbf\capturas'
            os.makedirs(base_dir, exist_ok=True)
            
            # Save complete raw packet
            raw_file = os.path.join(base_dir, f'packet_{timestamp}_pkt{packet_num:03d}_raw.bin')
            with open(raw_file, 'wb') as f:
                f.write(packet_bytes)
            
            # Save header (offset 0-87, 88 bytes)
            header_bytes = packet_bytes[HEADER_OFFSET:HEADER_OFFSET+88]
            header_file = os.path.join(base_dir, f'packet_{timestamp}_pkt{packet_num:03d}_header.bin')
            with open(header_file, 'wb') as f:
                f.write(header_bytes)
            
            # Save payload (offset 88-1431, 1344 bytes)
            payload_bytes = packet_bytes[PAYLOAD_OFFSET:PAYLOAD_OFFSET+PAYLOAD_SIZE]
            payload_file = os.path.join(base_dir, f'packet_{timestamp}_pkt{packet_num:03d}_payload.bin')
            with open(payload_file, 'wb') as f:
                f.write(payload_bytes)
            
            # Save parsed header as text
            header_txt_file = os.path.join(base_dir, f'packet_{timestamp}_pkt{packet_num:03d}_header.txt')
            with open(header_txt_file, 'w') as f:
                # Parse header fields
                timestamp_sec = struct.unpack('<Q', header_bytes[0:8])[0]
                timestamp_nsec = struct.unpack('<Q', header_bytes[8:16])[0]
                bd_id = struct.unpack('<B', header_bytes[16:17])[0]
                ch_id = struct.unpack('<B', header_bytes[17:18])[0]
                ch_adc = struct.unpack('<H', header_bytes[18:20])[0]
                fifo_flags = struct.unpack('<16I', header_bytes[20:84])

                try:
                    timestamp_str = datetime.fromtimestamp(timestamp_sec).strftime('%Y-%m-%d %H:%M:%S')
                    timestamp_str = f"{timestamp_str}.{timestamp_nsec:09d}"
                except (OSError, ValueError, OverflowError):
                    timestamp_str = f"INVALID_TIMESTAMP({timestamp_sec})"
                
                f.write(f"HEADER ANALYSIS - Packet {packet_num}\n")
                f.write("="*60 + "\n")
                payload_size = struct.unpack('<H', header_bytes[85:87])[0]

                f.write(f"Timestamp: {timestamp_sec}.{timestamp_nsec:09d}\n")
                f.write(f"Timestamp (str): {timestamp_str}\n")
                f.write(f"Payload size: {payload_size} ({payload_size * 16} bytes)\n")
                f.write(f"Board ID: 0x{bd_id:02X}\n")
                f.write(f"Channel ID: 0x{ch_id:02X}\n")
                f.write(f"ADC Channel: 0x{ch_adc:04X}\n")
                f.write(f"\nFIFO Flags (16 channels):\n")
                for i, flag in enumerate(fifo_flags):
                    f.write(f"  Ch{i:2d}: 0x{flag:08X}\n")
            
            print(f"[Unpacker] Saved packet {packet_num} to capturas/")
        except Exception as e:
            print(f"[Unpacker] ERROR saving packet {packet_num}: {e}")

    def _handle_pdu(self, msg):
        """Handle incoming PDU (one UDP datagram)"""
        if not pmt.is_pair(msg):
            return
        data = pmt.cdr(msg)
        if not pmt.is_u8vector(data):
            return
        packet_bytes = bytes(pmt.u8vector_elements(data))
        if len(packet_bytes) != PACKET_SIZE:
            return

        try:
            samples = self._simple_unpack(packet_bytes)
        except Exception:
            return

        self.sample_queue.append(samples)
        self.packets_received += 1

        if self.saved_packet_count < self.max_packets_to_save:
            self._save_packet_analysis(packet_bytes, self.saved_packet_count + 1)
            self.saved_packet_count += 1
            if self.saved_packet_count == self.max_packets_to_save:
                print(f"[Unpacker] Completed saving {self.max_packets_to_save} packets for analysis")

    def work(self, input_items, output_items):
        samples_produced = 0
        max_samples = len(output_items[0])

        while samples_produced + 21 <= max_samples:
            if self.current_samples is None:
                if not self.sample_queue:
                    break
                self.current_samples = self.sample_queue.popleft()

            samples = self.current_samples
            for ch in range(16):
                output_items[ch][samples_produced:samples_produced+21] = samples[:, ch]
            samples_produced += 21
            self.packets_parsed += 1
            self.current_samples = None

            if self.packets_parsed == 1:
                print(f"[Unpacker] First packet successfully parsed")
                print(f"  First sample Ch0: {samples[0, 0]:.0f}")
                print(f"  Sample shape: {samples.shape}")

            if self.packets_parsed >= self.stop_after_packets and not self.stopped:
                self.stopped = True
                print(f"\n[Unpacker] Reached {self.stop_after_packets} packets. Processing complete.")
                print(f"[Unpacker] Data saved to ciaa_ch0_5packets.dat")
                break

        if self.stopped:
            return samples_produced if samples_produced > 0 else -1

        return samples_produced

    def _simple_unpack(self, packet_bytes):
        """Unpack CIAA packet - OPTIMIZED with NumPy"""
        if len(packet_bytes) != PACKET_SIZE:
            raise ValueError(f"Invalid packet size: {len(packet_bytes)}")
        
        # Extract payload from offset 88
        payload = packet_bytes[PAYLOAD_OFFSET:PAYLOAD_OFFSET+PAYLOAD_SIZE]
        
        # Parse as uint32 array and reshape (MUCH faster than loops)
        words = np.frombuffer(payload, dtype=np.uint32)
        words = words.reshape((21, 16))
        
        # Use full 32-bit counter value (HI:LO)
#        samples = words.astype(np.float32)
        words_signed = words.astype(np.int32)
        samples = words_signed.astype(np.float32)
	
        
        return samples