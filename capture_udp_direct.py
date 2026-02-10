#!/usr/bin/env python3
"""
Direct UDP capture without GNU Radio
Receives CIAA packets and verifies structure
"""

import socket
import struct
import time
import sys

def capture_udp_packets(port=9999, num_packets=5):
    """Capture raw UDP packets directly"""
    print("="*70)
    print(f"Direct UDP Capture (port {port})")
    print("="*70)
    print(f"\nListening for {num_packets} packets...")
    print("Make sure CIAA is streaming (LAUNCH UDP Streaming button)")
    print()
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)  # 1MB buffer
    sock.bind(('0.0.0.0', port))
    sock.settimeout(10.0)  # 10 second timeout
    
    packets_received = 0
    
    try:
        for pkt_num in range(num_packets):
            print(f"Waiting for packet {pkt_num+1}/{num_packets}...", end='', flush=True)
            
            try:
                data, addr = sock.recvfrom(65536)  # Max UDP packet size
            except socket.timeout:
                print(f"\n✗ Timeout waiting for packet")
                break
            
            print(f" received {len(data)} bytes from {addr}")
            packets_received += 1
            
            # Parse packet structure
            if len(data) < 88:
                print(f"  ✗ Packet too small ({len(data)} bytes), expected >= 88")
                continue
            
            # Header parsing
            timestamp_sec = struct.unpack('<Q', data[0:8])[0]
            timestamp_nsec = struct.unpack('<Q', data[8:16])[0]
            bd_id = data[16]
            ch_id = data[17]
            ch_adc = struct.unpack('<H', data[18:20])[0]
            
            # FIFO flags
            fifo_flags = []
            for i in range(16):
                flag_offset = 20 + i*4
                flag = struct.unpack('<I', data[flag_offset:flag_offset+4])[0]
                fifo_flags.append(flag)
            
            payload_size = struct.unpack('<H', data[84:86])[0]
            
            print(f"  Timestamp: {timestamp_sec}.{timestamp_nsec:09d}")
            print(f"  Board ID: {bd_id}, Channel ID: {ch_id}, ADC: {ch_adc}")
            print(f"  Payload size: {payload_size} bytes")
            print(f"  Actual data size: {len(data)} bytes")
            
            # Check for overflow
            overflow_chs = [i for i, f in enumerate(fifo_flags) if (f & 0x4000)]
            if overflow_chs:
                print(f"  ⚠ OVERFLOW on channels: {overflow_chs}")
            
            # Parse first sample from payload (all 16 channels)
            if len(data) >= 88 + 64:  # Header + first 16 words
                payload = data[88:]
                first_sample = []
                
                for ch in range(16):
                    word_offset = ch * 4
                    if word_offset + 4 <= len(payload):
                        word = struct.unpack('<I', payload[word_offset:word_offset+4])[0]
                        hi_word = (word >> 16) & 0xFFFF
                        lo_word = word & 0xFFFF
                        
                        # Convert hi_word to signed 14-bit
                        if hi_word & 0x2000:
                            hi_signed = hi_word - 0x4000
                        else:
                            hi_signed = hi_word
                        
                        first_sample.append(hi_signed)
                
                print(f"  First sample (row 0):")
                print(f"    Ch0-7:  {first_sample[0:8]}")
                print(f"    Ch8-15: {first_sample[8:16]}")
                
                # Check counter pattern
                if len(set(first_sample[0:10])) == 1:
                    print(f"  ✓ Counter pattern: {first_sample[0]} = {hex(first_sample[0])}")
            
            print()
    
    except KeyboardInterrupt:
        print("\n\nCapture interrupted by user")
    
    finally:
        sock.close()
    
    print("="*70)
    print(f"Captured {packets_received} packets")
    print("="*70)
    
    return packets_received > 0


def main():
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "="*70)
    print("CIAA Direct UDP Packet Capture")
    print("="*70)
    print("\nThis script bypasses GNU Radio and captures UDP directly")
    print("to verify packet structure from CIAA\n")
    
    success = capture_udp_packets(port=9999, num_packets=5)
    
    if success:
        print("\n✓ UDP packets received successfully!")
        print("  Packet structure appears valid")
        print("  Problem is likely in GNU Radio processing chain")
    else:
        print("\n✗ No UDP packets received")
        print("  Check:")
        print("  1. CIAA is powered on and connected")
        print("  2. Network cable connected")
        print("  3. CIAA IP is 192.168.0.22")
        print("  4. PC IP is 192.168.0.x (same subnet)")
        print("  5. UDP streaming started on CIAA")


if __name__ == '__main__':
    main()
