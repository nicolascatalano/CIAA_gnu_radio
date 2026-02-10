#!/usr/bin/env python3
"""
Verificar que el código embebido en el .grc fue corregido
"""

import re

grc_file = r'f:\Proyectos\sist_adq_dbf\gnuradio\CIAA_UDP_Receiver_Working.grc'

with open(grc_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("="*70)
print("VERIFICACION DEL CODIGO EMBEBIDO EN EL .GRC")
print("="*70)

# Buscar el _source_code del bloque unpacker
match = re.search(r'_source_code: "(.*?)"', content, re.DOTALL)

if match:
    source_code = match.group(1)
    # Decodificar los escapes
    source_code = source_code.replace('\\n', '\n')
    
    print("\n🔍 Buscando línea crítica del parseo...\n")
    
    # Buscar la línea crítica
    if 'payload = packet_bytes[88:88+1344]' in source_code:
        print("❌ INCORRECTO - Todavía lee desde offset 88:")
        print("   payload = packet_bytes[88:88+1344]")
        print("\n⚠️  NECESITAS RECARGAR EL ARCHIVO .grc SI LO TENÍAS ABIERTO")
    elif 'PAYLOAD_OFFSET = 0' in source_code and 'payload = packet_bytes[PAYLOAD_OFFSET:PAYLOAD_OFFSET+PAYLOAD_SIZE]' in source_code:
        print("✅ CORRECTO - Lee desde offset 0:")
        print("   PAYLOAD_OFFSET = 0")
        print("   payload = packet_bytes[PAYLOAD_OFFSET:PAYLOAD_OFFSET+PAYLOAD_SIZE]")
    elif 'payload = packet_bytes[0:1344]' in source_code:
        print("✅ CORRECTO - Lee desde offset 0:")
        print("   payload = packet_bytes[0:1344]")
    else:
        print("⚠️  No se encontró la línea de parseo - revisar manualmente")
    
    # Verificar optimización NumPy
    print("\n🔍 Verificando optimización NumPy...\n")
    
    if 'for sample_idx in range(21):' in source_code and 'for ch_idx in range(16):' in source_code:
        print("❌ LOOPS Python - NO optimizado")
        print("   (336 iteraciones por paquete)")
    elif 'np.frombuffer(payload, dtype=np.uint32)' in source_code:
        print("✅ NumPy vectorizado - OPTIMIZADO")
        print("   (3 operaciones por paquete, ~10-20x más rápido)")
    else:
        print("⚠️  No se pudo determinar el método de parseo")
    
    # Verificar estadísticas
    print("\n🔍 Verificando estadísticas cada 500 paquetes...\n")
    
    if 'packets_parsed % 500 == 0' in source_code:
        print("✅ Estadísticas cada 500 paquetes HABILITADAS")
        print("   Verás: [Unpacker] Packets: 500, Buffer: xxx, Drop rate: x.xx%")
    else:
        print("❌ Estadísticas NO encontradas")
    
    # Verificar sync correcto
    print("\n🔍 Verificando búsqueda de sync...\n")
    
    if 'timestamp_sec = struct.unpack' in source_code and 'offset+1348' in source_code:
        print("✅ Sync busca timestamp en offset 1348 (correcto)")
    elif 'payload_size = struct.unpack' in source_code and 'offset+84' in source_code:
        print("❌ Sync busca en offset 84 (incorrecto)")
    else:
        print("⚠️  No se pudo determinar método de sync")

else:
    print("❌ No se encontró el _source_code en el archivo .grc")

print("\n" + "="*70)
print("SIGUIENTE PASO:")
print("="*70)
print("""
1. Si ves ❌ INCORRECTO:
   → Cierra GNU Radio Companion completamente
   → Vuelve a abrir el archivo .grc
   → El código debería estar corregido

2. Si ves ✅ CORRECTO:
   → Abre GNU Radio Companion
   → Carga CIAA_UDP_Receiver_Working.grc
   → Click en Run (▶️) 
   → Verifica los mensajes de estadísticas cada 500 paquetes
""")
