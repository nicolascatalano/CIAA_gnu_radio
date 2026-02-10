#!/usr/bin/env python3
"""
Analyze CIAA UDP capture and output data files
Diagnoses packet structure and channel data integrity
"""

import numpy as np
import struct
import sys
import os

def analyze_udp_dump(filename, max_packets=10):
    """Analyze raw UDP packet dump"""
    print(f"\n{'='*70}")
    print(f"UDP Dump Analysis: {filename}")
    print(f"{'='*70}")
    
    if not os.path.exists(filename):
        print(f"ERROR: File not found: {filename}")
        return None
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    file_size = len(data)
    packet_size = 1436
    num_packets = file_size // packet_size
    
    print(f"File size: {file_size:,} bytes")
    print(f"Expected packet size: {packet_size} bytes")
    print(f"Number of complete packets: {num_packets}")
    print(f"Remainder bytes: {file_size % packet_size}")
    
    if num_packets == 0:
        print("ERROR: No complete packets found!")
        return None
    
    print(f"\nAnalyzing first {min(max_packets, num_packets)} packets...")
    
    packet_data = []
    for pkt_idx in range(min(max_packets, num_packets)):
        offset = pkt_idx * packet_size
        packet = data[offset:offset+packet_size]
        
        # Header (88 bytes)
        header = packet[:88]
        timestamp_sec = struct.unpack('<Q', header[0:8])[0]
        timestamp_nsec = struct.unpack('<Q', header[8:16])[0]
        bd_id = header[16]
        ch_id = header[17]
        
        # FIFO flags (64 bytes, 16 x 4-byte words)
        fifo_flags = []
        for i in range(16):
            flag_offset = 20 + i*4
            flag = struct.unpack('<I', header[flag_offset:flag_offset+4])[0]
            fifo_flags.append(flag)
        
        payload_size = struct.unpack('<H', header[84:86])[0]
        
        # Payload (1344 bytes = 21 samples × 16 channels × 4 bytes)
        payload = packet[88:88+1344]
        
        print(f"\n--- Packet #{pkt_idx} ---")
        print(f"  Timestamp: {timestamp_sec}.{timestamp_nsec:09d}")
        print(f"  Board ID: {bd_id}, Channel ID: {ch_id}")
        print(f"  Payload size: {payload_size} bytes")
        
        # Check FIFO overflow flags (bit 14)
        overflow_channels = [i for i, flag in enumerate(fifo_flags) if (flag & 0x4000)]
        if overflow_channels:
            print(f"  ⚠ OVERFLOW on channels: {overflow_channels}")
        
        # Parse first sample (all 16 channels)
        sample_0 = []
        for ch in range(16):
            word_offset = ch * 4
            word = struct.unpack('<I', payload[word_offset:word_offset+4])[0]
            hi_word = (word >> 16) & 0xFFFF
            lo_word = word & 0xFFFF
            
            # Convert to signed 14-bit
            if hi_word & 0x2000:
                value = hi_word - 0x4000
            else:
                value = hi_word
            
            sample_0.append(value)
        
        print(f"  First sample (row 0):")
        print(f"    Ch0-7:  {sample_0[0:8]}")
        print(f"    Ch8-15: {sample_0[8:16]}")
        
        # Check for counter pattern (all channels should have same value)
        if len(set(sample_0[0:10])) == 1:  # ADC1 channels identical
            print(f"  ✓ Counter pattern detected: {hex(sample_0[0])}")
        
        # Check ADC2 offset issue (Ch10-15 should be sample_0[0] or sample_0[0]+1)
        adc2_values = sample_0[10:16]
        expected = sample_0[0]
        adc2_match = all(v in [expected, expected+1] for v in adc2_values)
        if adc2_match:
            offsets = [v - expected for v in adc2_values]
            print(f"  ADC2 offset: {offsets} (expected 0 or 1)")
        
        packet_data.append({
            'timestamp': (timestamp_sec, timestamp_nsec),
            'bd_id': bd_id,
            'ch_id': ch_id,
            'fifo_flags': fifo_flags,
            'first_sample': sample_0
        })
    
    return packet_data


def analyze_channel_output(filename, max_samples=1000):
    """Analyze channel output file (.dat float32 format)"""
    print(f"\n{'='*70}")
    print(f"Channel Output Analysis: {filename}")
    print(f"{'='*70}")
    
    if not os.path.exists(filename):
        print(f"ERROR: File not found: {filename}")
        return None
    
    # Read as float32
    try:
        data = np.fromfile(filename, dtype=np.float32)
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return None
    
    num_samples = len(data)
    print(f"Total samples: {num_samples:,}")
    print(f"File size: {num_samples * 4:,} bytes")
    
    if num_samples == 0:
        print("ERROR: No samples found!")
        return None
    
    # Statistics
    print(f"\nStatistics:")
    print(f"  Min:  {np.min(data):.2f}")
    print(f"  Max:  {np.max(data):.2f}")
    print(f"  Mean: {np.mean(data):.2f}")
    print(f"  Std:  {np.std(data):.2f}")
    
    # Check for counter pattern
    first_n = min(max_samples, num_samples)
    sample_subset = data[:first_n].astype(int)
    
    # Check if incrementing
    diffs = np.diff(sample_subset)
    increment_by_1 = np.sum(diffs == 1)
    increment_other = np.sum(diffs != 1)
    
    print(f"\nFirst {first_n} samples analysis:")
    print(f"  Increments by 1: {increment_by_1} ({100*increment_by_1/(first_n-1):.1f}%)")
    print(f"  Other increments: {increment_other} ({100*increment_other/(first_n-1):.1f}%)")
    
    if increment_by_1 > 0.9 * (first_n - 1):
        print(f"  ✓ Counter pattern confirmed!")
        print(f"  Starting value: {int(sample_subset[0])} = {hex(int(sample_subset[0]))}")
    
    # Show first 20 samples
    print(f"\nFirst 20 samples:")
    for i in range(min(20, num_samples)):
        print(f"  [{i:3d}] {int(data[i]):6d} = {hex(int(data[i]) & 0xFFFF):>6s}")
    
    return data


def main():
    print("\n" + "="*70)
    print("CIAA UDP Capture Analysis Tool")
    print("="*70)
    
    # Analyze UDP dump
    udp_file = 'ciaa_udp_dump.bin'
    packet_data = analyze_udp_dump(udp_file, max_packets=5)
    
    # Analyze channel 0 output
    ch0_file = 'ciaa_ch0.dat'
    channel_data = analyze_channel_output(ch0_file, max_samples=1000)
    
    # Cross-validation
    if packet_data and channel_data is not None:
        print(f"\n{'='*70}")
        print("Cross-Validation")
        print(f"{'='*70}")
        
        # Extract expected values from UDP packets
        expected_values = []
        for pkt in packet_data:
            # Each packet has 21 samples for channel 0
            expected_values.append(pkt['first_sample'][0])
        
        # Compare with output file
        actual_values = channel_data[:len(expected_values)].astype(int)
        
        print(f"Comparing first {len(expected_values)} samples...")
        print(f"Expected (from UDP): {expected_values}")
        print(f"Actual (from .dat):  {list(actual_values)}")
        
        matches = sum(1 for e, a in zip(expected_values, actual_values) if e == a)
        print(f"Matches: {matches}/{len(expected_values)} ({100*matches/len(expected_values):.1f}%)")
    
    print(f"\n{'='*70}")
    print("Analysis complete!")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    # Change to gnuradio directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    main()
