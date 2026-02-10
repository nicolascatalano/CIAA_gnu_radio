#!/usr/bin/env python3
"""
Test r\u00e1pido del parser corregido con captura real
"""

import sys
sys.path.insert(0, r'f:\Proyectos\sist_adq_dbf\gnuradio_streaming')
import packet_parser
import struct

# Cargar paquete de captura
capture_file = r'f:\Proyectos\sist_adq_dbf\capturas\udp_capture_20260203_110045_pkt004.bin'

with open(capture_file, 'rb') as f:
    packet_data = f.read()

print(f"\u2705 Cargado paquete: {len(packet_data)} bytes")
print(f"\nAnalizando estructura del paquete...")

# Parsear con el nuevo parser
parser = packet_parser.CIAAPacketParser(verbose=True)

try:
    header, samples = parser.parse_packet(packet_data, data_type='int16', warn_overflow=True)
    
    print(f"\n\u2705 PARSEO EXITOSO!")
    print(f"\n=== HEADER ===")
    print(f"Timestamp: {header['timestamp_sec']}.{header['timestamp_nsec']:09d}")
    print(f"Board ID: 0x{header['bd_id']:02X}")
    print(f"Channel ID: {header['ch_id']}")
    print(f"ADC Channel: {header['ch_adc']}")
    print(f"CLK Divider: {header['clk_divider']}")
    
    # Verificar FIFO flags
    overflow_channels = []
    for ch, flags in enumerate(header['fifo_flags']):
        if flags & (1 << 14):  # Bit 14 = overflow
            overflow_channels.append(ch)
    
    if overflow_channels:
        print(f"\u26a0\ufe0f  OVERFLOW detectado en canales: {overflow_channels}")
    else:
        print(f"\u2705 Sin OVERFLOW")
    
    print(f"\n=== PAYLOAD ===")
    print(f"Samples shape: {samples.shape}")
    print(f"\nPrimeros 5 samples de cada canal:")
    for ch in range(min(4, 16)):
        print(f"  Ch{ch}: {samples[:5, ch]}")
    
    # Verificar si es patr\u00f3n contador
    print(f"\n=== AN\u00c1LISIS DE PATR\u00d3N ===")
    # Chequear si hay incremento entre samples (patr\u00f3n contador)
    diffs_ch0 = samples[1:, 0] - samples[:-1, 0]
    is_counter = all(d == 1.0 for d in diffs_ch0)
    
    if is_counter:
        print(f"\u2705 Patr\u00f3n CONTADOR detectado (incrementa +1 por sample)")
    else:
        print(f"\u2139\ufe0f  Patr\u00f3n ADC u otro (no es contador simple)")
        print(f"   Diferencias Ch0: {diffs_ch0[:5]}")
    
    # Estadísticas
    print(f"\n=== ESTAD\u00cdSTICAS Ch0 ===")
    print(f"Min: {samples[:, 0].min():.0f}")
    print(f"Max: {samples[:, 0].max():.0f}")
    print(f"Mean: {samples[:, 0].mean():.1f}")
    print(f"Std: {samples[:, 0].std():.1f}")

except Exception as e:
    print(f"\n\u274c ERROR en parseo: {e}")
    import traceback
    traceback.print_exc()
    
    # Debug: mostrar bytes relevantes
    print(f"\n=== DEBUG: Bytes clave ===")
    print(f"Bytes 0-16 (inicio payload): {packet_data[0:16].hex()}")
    print(f"Bytes 1344-1347 (CRC/unknown): {packet_data[1344:1348].hex()}")
    print(f"Bytes 1348-1364 (inicio header): {packet_data[1348:1364].hex()}")
    
    # Intentar leer timestamps manualmente
    try:
        ts_sec = struct.unpack('<Q', packet_data[1348:1356])[0]
        ts_nsec = struct.unpack('<Q', packet_data[1356:1364])[0]
        print(f"\nTimestamps desde offset 1348:")
        print(f"  Seconds: {ts_sec} ({ts_sec:016x})")
        print(f"  Nanosec: {ts_nsec} ({ts_nsec:016x})")
    except:
        pass

print("\n" + "="*50)
