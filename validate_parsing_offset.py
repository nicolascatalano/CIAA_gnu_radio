#!/usr/bin/env python3
"""
Validaci\u00f3n r\u00e1pida del parseo corregido
Compara offset 0 vs offset 88 para demostrar cu\u00e1l es el correcto
"""

import struct
import numpy as np

# Cargar captura
capture_file = r'f:\Proyectos\sist_adq_dbf\capturas\udp_capture_20260203_110045_pkt004.bin'

with open(capture_file, 'rb') as f:
    packet = f.read()

print("="*70)
print("VALIDACI\u00d3N DEL OFFSET DE PARSEO")
print("="*70)

print(f"\nPaquete cargado: {len(packet)} bytes\n")

# Intentar parsear desde offset 88 (INCORRECTO - forma antigua)
print("\u274c PARSEO INCORRECTO (offset 88 - forma antigua):")
print("-" * 70)
payload_wrong = packet[88:88+1344]
words_wrong = np.frombuffer(payload_wrong, dtype=np.uint32).reshape((21, 16))
samples_wrong = (words_wrong & 0xFFFF).astype(np.int16)

print(f"Primeros 5 samples Ch0: {samples_wrong[:5, 0]}")
print(f"Primeros 5 samples Ch1: {samples_wrong[:5, 1]}")

# Verificar si es contador
diffs = samples_wrong[1:5, 0] - samples_wrong[:4, 0]
is_counter_wrong = all(d == 1 for d in diffs)
print(f"Es contador? {is_counter_wrong}")
print(f"Diferencias: {diffs}")

# Parsear desde offset 0 (CORRECTO - forma nueva)
print(f"\n\u2705 PARSEO CORRECTO (offset 0 - forma nueva):")
print("-" * 70)
payload_correct = packet[0:1344]
words_correct = np.frombuffer(payload_correct, dtype=np.uint32).reshape((21, 16))
samples_correct = (words_correct & 0xFFFF).astype(np.int16)

print(f"Primeros 5 samples Ch0: {samples_correct[:5, 0]}")
print(f"Primeros 5 samples Ch1: {samples_correct[:5, 1]}")

# Verificar si es contador
diffs_correct = samples_correct[1:5, 0] - samples_correct[:4, 0]
is_counter_correct = all(d == 1 for d in diffs_correct)
print(f"Es contador? {is_counter_correct}")
print(f"Diferencias: {diffs_correct}")

# Validar header
print(f"\n\ud83d\udccb VALIDACI\u00d3N DEL HEADER (offset 1348):")
print("-" * 70)
timestamp_sec = struct.unpack('<Q', packet[1348:1356])[0]
timestamp_nsec = struct.unpack('<Q', packet[1356:1364])[0]
bd_id = struct.unpack('<B', packet[1364:1365])[0]
ch_id = struct.unpack('<B', packet[1365:1366])[0]

print(f"Timestamp: {timestamp_sec}.{timestamp_nsec:09d}")

from datetime import datetime
try:
    dt = datetime.fromtimestamp(timestamp_sec)
    print(f"Fecha: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Board ID: 0x{bd_id:02X}")
    print(f"Channel ID: {ch_id}")
    
    # Validar que el timestamp sea razonable
    if 2020 <= dt.year <= 2030:
        print(f"\u2705 Timestamp v\u00e1lido (a\u00f1o {dt.year})")
    else:
        print(f"\u274c Timestamp inv\u00e1lido (a\u00f1o {dt.year})")
except:
    print(f"\u274c Error al parsear timestamp")

print(f"\n" + "="*70)
print("CONCLUSI\u00d3N:")
print("="*70)

if is_counter_correct and not is_counter_wrong:
    print("\u2705 El parseo CORRECTO (offset 0) detecta el patr\u00f3n contador")
    print("\u274c El parseo INCORRECTO (offset 88) NO detecta el patr\u00f3n")
    print(f"\n\u27a1\ufe0f  El unpacker DEBE leer desde offset 0, NO desde 88")
elif is_counter_correct:
    print("\u2705 Ambos detectan contador, pero offset 0 es el correcto seg\u00fan")
    print("   la estructura documentada [PAYLOAD][CRC][HEADER]")
else:
    print("\u26a0\ufe0f  Revisar - puede no ser patr\u00f3n contador")

print("\n")
