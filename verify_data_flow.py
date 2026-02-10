#!/usr/bin/env python3
"""
Verify data flow through GNU Radio flowgraph
Compare UDP dump vs channel output to find where data gets corrupted
"""

import numpy as np
import struct
import os

def analyze_udp_dump_as_stream():
    """Analyze ciaa_udp_dump.bin as raw 32-bit word stream (no packet structure)"""
    print("\n" + "="*70)
    print("Analysis: ciaa_udp_dump.bin (raw stream interpretation)")
    print("="*70)
    
    with open('ciaa_udp_dump.bin', 'rb') as f:
        data = f.read()
    
    num_words = len(data) // 4
    print(f"File size: {len(data):,} bytes")
    print(f"Number of 32-bit words: {num_words:,}")
    
    # Parse as stream of 32-bit words
    words = []
    for i in range(min(100, num_words)):
        offset = i * 4
        word = struct.unpack('<I', data[offset:offset+4])[0]
        hi_word = (word >> 16) & 0xFFFF
        lo_word = word & 0xFFFF
        
        # Convert hi_word to signed 14-bit
        if hi_word & 0x2000:
            hi_signed = hi_word - 0x4000
        else:
            hi_signed = hi_word
        
        # Convert lo_word to signed 14-bit  
        if lo_word & 0x2000:
            lo_signed = lo_word - 0x4000
        else:
            lo_signed = lo_word
        
        words.append({
            'raw': word,
            'hi_word': hi_word,
            'lo_word': lo_word,
            'hi_signed': hi_signed,
            'lo_signed': lo_signed
        })
    
    print("\nFirst 20 words (as 32-bit stream):")
    print("Idx  Raw Word     Hi(hex)  Hi(dec)   Lo(hex)  Lo(dec)")
    print("-" * 65)
    for i, w in enumerate(words[:20]):
        print(f"{i:3d}  0x{w['raw']:08x}  0x{w['hi_word']:04x}  {w['hi_signed']:6d}   0x{w['lo_word']:04x}  {w['lo_signed']:6d}")
    
    # Check for counter pattern in hi_word
    hi_values = [w['hi_signed'] for w in words[:50]]
    if len(set(hi_values[:10])) <= 2:  # All similar values
        print(f"\n✓ Hi-word shows constant value: {hi_values[0]} = 0x{words[0]['hi_word']:04x}")
    
    # Check for counter pattern in lo_word
    lo_values = [w['lo_signed'] for w in words[:50]]
    lo_diffs = [lo_values[i+1] - lo_values[i] for i in range(len(lo_values)-1)]
    increments = sum(1 for d in lo_diffs if d in [1, 2])
    
    print(f"\nLo-word pattern:")
    print(f"  First value: {lo_values[0]} = 0x{words[0]['lo_word']:04x}")
    print(f"  Increments by 1-2: {increments}/{len(lo_diffs)} ({100*increments/len(lo_diffs):.1f}%)")
    
    if increments > 0.8 * len(lo_diffs):
        print(f"  ✓ Lo-word is incrementing counter!")
    
    return words


def analyze_channel_output():
    """Analyze ciaa_ch0.dat output"""
    print("\n" + "="*70)
    print("Analysis: ciaa_ch0.dat (unpacker output)")
    print("="*70)
    
    data = np.fromfile('ciaa_ch0.dat', dtype=np.float32)
    print(f"Total samples: {len(data):,}")
    print(f"File size: {len(data) * 4:,} bytes")
    
    print("\nFirst 20 samples:")
    for i in range(min(20, len(data))):
        val_int = int(data[i])
        print(f"  [{i:3d}] {data[i]:8.1f}  (int: {val_int:6d} = 0x{val_int & 0xFFFF:04x})")
    
    # Check pattern
    int_values = data[:50].astype(int)
    diffs = np.diff(int_values)
    increments = np.sum((diffs == 1) | (diffs == 2))
    
    print(f"\nPattern analysis:")
    print(f"  Increments by 1-2: {increments}/{len(diffs)} ({100*increments/len(diffs):.1f}%)")
    
    return data


def cross_check():
    """Cross-check if channel output matches lo_word from UDP dump"""
    print("\n" + "="*70)
    print("CROSS-CHECK: Finding data source")
    print("="*70)
    
    # Load both files
    with open('ciaa_udp_dump.bin', 'rb') as f:
        udp_data = f.read()
    
    ch_data = np.fromfile('ciaa_ch0.dat', dtype=np.float32)
    
    # Extract first 20 words from UDP dump
    print("\nComparing first 20 values:")
    print("Idx  UDP Hi-word  UDP Lo-word  Channel Output  Match?")
    print("-" * 65)
    
    matches_hi = 0
    matches_lo = 0
    
    for i in range(min(20, len(ch_data), len(udp_data)//4)):
        offset = i * 4
        word = struct.unpack('<I', udp_data[offset:offset+4])[0]
        hi_word = (word >> 16) & 0xFFFF
        lo_word = word & 0xFFFF
        
        # Convert to signed
        if hi_word & 0x2000:
            hi_signed = hi_word - 0x4000
        else:
            hi_signed = hi_word
            
        if lo_word & 0x2000:
            lo_signed = lo_word - 0x4000
        else:
            lo_signed = lo_word
        
        ch_value = int(ch_data[i])
        
        match_hi = "HI!" if ch_value == hi_signed else ""
        match_lo = "LO!" if ch_value == lo_signed else ""
        
        if ch_value == hi_signed:
            matches_hi += 1
        if ch_value == lo_signed:
            matches_lo += 1
        
        print(f"{i:3d}  {hi_signed:6d}       {lo_signed:6d}       {ch_value:6d}          {match_hi}{match_lo}")
    
    print(f"\nMatches with hi_word: {matches_hi}/20")
    print(f"Matches with lo_word: {matches_lo}/20")
    
    if matches_hi > matches_lo:
        print("\n✓ CONCLUSION: Unpacker is correctly extracting HI_WORD")
    elif matches_lo > matches_hi:
        print("\n✗ CONCLUSION: Unpacker is INCORRECTLY extracting LO_WORD")
        print("   BUG: Code should use hi_word but is using lo_word!")
    else:
        print("\n? CONCLUSION: Data doesn't match either field - possible corruption")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "="*70)
    print("GNU Radio CIAA Data Flow Verification")
    print("="*70)
    
    words = analyze_udp_dump_as_stream()
    ch_data = analyze_channel_output()
    cross_check()
    
    print("\n" + "="*70)
    print("Analysis complete")
    print("="*70)


if __name__ == '__main__':
    main()
