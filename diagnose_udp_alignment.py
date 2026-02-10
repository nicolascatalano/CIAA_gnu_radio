#!/usr/bin/env python3
"""
Diagnose UDP packet alignment issues in GNU Radio capture
"""

import numpy as np
import struct
import sys

def find_packet_sync(data, max_search=10000):
    """Search for valid packet boundaries by looking for header patterns"""
    print(f"\nSearching for packet sync pattern in first {max_search} bytes...")
    
    packet_size = 1436
    header_size = 88
    payload_size_expected = 1344
    
    # Try different offsets
    for offset in range(min(max_search, len(data) - packet_size)):
        try:
            # Try to parse header at this offset
            header = data[offset:offset+header_size]
            
            # Check payload_size field (bytes 84-86)
            payload_size = struct.unpack('<H', header[84:86])[0]
            
            # Valid payload size should be 1344
            if payload_size == payload_size_expected:
                # Check if timestamp makes sense (not crazy values)
                timestamp_sec = struct.unpack('<Q', header[0:8])[0]
                
                # Reasonable timestamp (Unix time between 2020-2030)
                if 1577836800 < timestamp_sec < 1893456000:
                    print(f"\n✓ Found valid packet at offset {offset}")
                    print(f"  Timestamp: {timestamp_sec}")
                    print(f"  Payload size: {payload_size}")
                    
                    # Parse first data word from payload
                    payload = data[offset+header_size:offset+header_size+1344]
                    if len(payload) >= 64:  # At least 16 channels × 4 bytes
                        first_values = []
                        for ch in range(16):
                            word_offset = ch * 4
                            word = struct.unpack('<I', payload[word_offset:word_offset+4])[0]
                            hi_word = (word >> 16) & 0xFFFF
                            # Convert to signed 14-bit
                            if hi_word & 0x2000:
                                value = hi_word - 0x4000
                            else:
                                value = hi_word
                            first_values.append(value)
                        
                        print(f"  First sample: {first_values[0:8]}")
                        print(f"               {first_values[8:16]}")
                        
                        # Check if counter pattern
                        if len(set(first_values[0:10])) == 1:
                            print(f"  ✓ Counter pattern: {first_values[0]} = {hex(first_values[0])}")
                        
                        return offset
        except Exception:
            continue
    
    print("✗ No valid packet sync found!")
    return None


def analyze_raw_bytes(data, max_bytes=200):
    """Show raw byte structure"""
    print(f"\nRaw byte dump (first {max_bytes} bytes):")
    print("Offset   Hex                                          ASCII")
    print("-" * 70)
    
    for i in range(0, min(max_bytes, len(data)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"{i:06x}   {hex_str:<48} {ascii_str}")


def check_packet_alignment(filename):
    """Main diagnostic function"""
    print("=" * 70)
    print("UDP Packet Alignment Diagnostic")
    print("=" * 70)
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"\nFile: {filename}")
    print(f"Size: {len(data):,} bytes")
    
    # Show raw bytes
    analyze_raw_bytes(data, max_bytes=256)
    
    # Find sync
    sync_offset = find_packet_sync(data, max_search=50000)
    
    if sync_offset is not None and sync_offset > 0:
        print(f"\n⚠ WARNING: Packet data starts at offset {sync_offset}, not 0!")
        print(f"   There are {sync_offset} bytes of header/garbage before first packet.")
        print(f"\n   This explains why unpacker is misaligned!")
    elif sync_offset == 0:
        print(f"\n✓ Packets are aligned at offset 0 (correct)")
    
    # Try parsing as if packets are at offset 0 anyway
    print(f"\n" + "=" * 70)
    print("Attempting parse at offset 0 (current unpacker behavior):")
    print("=" * 70)
    
    packet_size = 1436
    if len(data) >= packet_size:
        packet = data[0:packet_size]
        header = packet[0:88]
        
        print(f"\nHeader fields (offset 0):")
        print(f"  Bytes 0-7   (timestamp_sec):  {struct.unpack('<Q', header[0:8])[0]}")
        print(f"  Bytes 8-15  (timestamp_nsec): {struct.unpack('<Q', header[8:16])[0]}")
        print(f"  Byte 16     (bd_id):          {header[16]}")
        print(f"  Byte 17     (ch_id):          {header[17]}")
        print(f"  Bytes 84-85 (payload_size):   {struct.unpack('<H', header[84:86])[0]}")
        
        payload = packet[88:88+1344]
        print(f"\nFirst 10 words of 'payload' (really bytes 88-127):")
        for i in range(10):
            word_offset = i * 4
            if word_offset + 4 <= len(payload):
                word = struct.unpack('<I', payload[word_offset:word_offset+4])[0]
                print(f"  Word {i}: 0x{word:08x} = {word:10d}  (hi=0x{(word>>16):04x}, lo=0x{(word&0xFFFF):04x})")
    
    return sync_offset


def main():
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    filename = 'ciaa_udp_dump.bin'
    sync_offset = check_packet_alignment(filename)
    
    print(f"\n" + "=" * 70)
    if sync_offset == 0:
        print("DIAGNOSIS: Packets are correctly aligned")
        print("Problem must be in unpacker logic itself")
    elif sync_offset is not None:
        print(f"DIAGNOSIS: Packets start at offset {sync_offset}")
        print("GNU Radio socket PDU may be prepending metadata/headers")
        print(f"SOLUTION: Skip first {sync_offset} bytes in unpacker")
    else:
        print("DIAGNOSIS: Cannot find valid CIAA packet structure")
        print("File may be corrupted or not contain CIAA packets")
    print("=" * 70)


if __name__ == '__main__':
    main()
