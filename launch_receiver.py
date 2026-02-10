#!/usr/bin/env python3
"""
Script para lanzar CIAA_UDP_Receiver_Working.grc
Regenera el .py y ejecuta el flowgraph
"""

import os
import subprocess
import sys

# Cambiar al directorio de gnuradio
os.chdir(r'f:\Proyectos\sist_adq_dbf\gnuradio')

print("="*60)
print("  CIAA UDP Receiver - Flowgraph Launcher")
print("="*60)
print(f"\n📁 Directorio: {os.getcwd()}")
print(f"🔧 Regenerando Python desde GRC...")

# Regenerar el archivo .py desde el .grc
try:
    result = subprocess.run(
        ['grcc', 'CIAA_UDP_Receiver_Working.grc'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print(f"✅ Flowgraph regenerado correctamente")
    else:
        print(f"⚠️  Advertencia al regenerar:")
        if result.stderr:
            print(result.stderr)
        print("\n🔄 Usando archivo .py existente...")
        
except FileNotFoundError:
    print(f"⚠️  'grcc' no encontrado. Usando archivo .py existente...")
except Exception as e:
    print(f"⚠️  Error al regenerar: {e}")
    print(f"🔄 Usando archivo .py existente...")

print(f"\n▶️  Ejecutando flowgraph...")
print(f"="*60)
print(f"\n📡 Esperando paquetes UDP en puerto 9999...")
print(f"   (Inicia la CIAA o el script send_test_packets.py)\n")

# Ejecutar el flowgraph
try:
    subprocess.run([sys.executable, 'CIAA_UDP_Receiver_Working.py'])
except KeyboardInterrupt:
    print(f"\n\n✅ Flowgraph detenido por el usuario")
except Exception as e:
    print(f"\n❌ Error al ejecutar: {e}")
