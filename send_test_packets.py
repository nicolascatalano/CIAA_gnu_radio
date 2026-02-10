#!/usr/bin/env python3
"""
Test del flowgraph CIAA_UDP_Receiver_Working con captura real
Lee la captura y simula paquetes UDP
"""

import sys
import time
import socket

# Cargar captura
capture_file = r'f:\Proyectos\sist_adq_dbf\capturas\udp_capture_20260203_110045_pkt004.bin'

with open(capture_file, 'rb') as f:
    packet_data = f.read()

print(f"✅ Captura cargada: {len(packet_data)} bytes")

# Enviar paquetes a localhost:9999 para que GNU Radio los reciba
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
target = ('127.0.0.1', 9999)

print(f"\n📡 Enviando paquetes a {target[0]}:{target[1]}")
print(f"   (Inicia GNU Radio para recibirlos)")
print(f"\nPresiona Ctrl+C para detener...\n")

packet_count = 0
try:
    while True:
        sock.sendto(packet_data, target)
        packet_count += 1
        
        if packet_count % 100 == 0:
            print(f"Paquetes enviados: {packet_count}")
        
        time.sleep(0.001)  # 1ms entre paquetes (~1000 pkt/s)
        
except KeyboardInterrupt:
    print(f"\n\n✅ Enviados {packet_count} paquetes total")
    sock.close()
