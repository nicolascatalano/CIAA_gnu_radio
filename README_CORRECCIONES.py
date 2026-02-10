#!/usr/bin/env python3
"""
INSTRUCCIONES para probar el flowgraph corregido
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║  CIAA UDP Receiver - Flowgraph Corregido                       ║
╚════════════════════════════════════════════════════════════════╝

✅ CORRECCIONES APLICADAS:

1. ✅ packet_parser.py - Header ahora se lee desde offset 1348
2. ✅ CIAA_UDP_Receiver_Working_epy_block_ciaa_unpacker.py - Payload desde offset 0
3. ✅ File sinks deshabilitados (no guarda archivos)
4. ✅ Parser validado con captura real

═══════════════════════════════════════════════════════════════════

📋 CÓMO PROBAR:

OPCIÓN A - Con captura de prueba (LOCAL):
──────────────────────────────────────────

1. Abrir 2 terminales:

   Terminal 1:
   > cd f:\\Proyectos\\sist_adq_dbf\\gnuradio
   > python send_test_packets.py
   
   Terminal 2:
   > cd f:\\Proyectos\\sist_adq_dbf\\gnuradio
   > gnuradio-companion CIAA_UDP_Receiver_Working.grc
   
2. En GNU Radio Companion:
   - Click en ▶️ (Run) o presiona F6
   - Deberías ver el patrón contador incrementando en el gráfico

═══════════════════════════════════════════════════════════════════

OPCIÓN B - Con CIAA en streaming (TIEMPO REAL):
────────────────────────────────────────────────

1. Configurar la CIAA para enviar a tu PC:

   En la CIAA (via SSH):
   $ cd /mnt/currentVersions
   $ echo "192.168.0.100 9999 10000" > client_config
   $ ./sist_adq_crc.elf client_config
   
   (Reemplazar 192.168.0.100 con tu IP)

2. En tu PC:
   > cd f:\\Proyectos\\sist_adq_dbf\\gnuradio
   > gnuradio-companion CIAA_UDP_Receiver_Working.grc
   
3. Click en ▶️ (Run)

═══════════════════════════════════════════════════════════════════

🔍 QUÉ VERIFICAR:

✅ En el gráfico de tiempo (Time Sink):
   - Canales 0-3 deberían mostrar señales
   - Con modo CONTADOR: línea ascendente constante
   - Con ADC: señales variables

✅ En el gráfico de frecuencia (Freq Sink):
   - Espectro de las señales
   - Con contador: pico DC + componentes periódicas

✅ En la consola:
   - Mensajes del unpacker cada 100 paquetes
   - "[Unpacker] First packet successfully parsed"
   - Sin mensajes de error de parseo

═══════════════════════════════════════════════════════════════════

⚠️  TROUBLESHOOTING:

Si ves errores como "Invalid packet size":
→ El sync de paquetes no está funcionando
→ Verificar que la CIAA está enviando a puerto 9999

Si los gráficos están congelados:
→ No están llegando paquetes
→ Verificar firewall de Windows
→ Verificar que el puerto 9999 está libre

Si el patrón no tiene sentido:
→ Verificar modo debug de la CIAA (debe ser 0xF para contador)
→ Ver qué está configurado en la CIAA con:
   ./axi_rw_test.elf r 43c00080  # DEBUG_Control

═══════════════════════════════════════════════════════════════════

📁 ARCHIVOS RELEVANTES:

- CIAA_UDP_Receiver_Working.grc  → Flowgraph principal
- CIAA_UDP_Receiver_Working_epy_block_ciaa_unpacker.py  → Bloque unpacker
- packet_parser.py  → Parser de paquetes (compartido)
- test_parser_fix.py  → Test unitario del parser

═══════════════════════════════════════════════════════════════════
""")

# Verificar que los archivos existen
import os

files_to_check = [
    'CIAA_UDP_Receiver_Working.grc',
    'CIAA_UDP_Receiver_Working_epy_block_ciaa_unpacker.py',
    '../gnuradio_streaming/packet_parser.py',
    'send_test_packets.py'
]

print("📋 Verificación de archivos:\n")

os.chdir(r'f:\Proyectos\sist_adq_dbf\gnuradio')
all_ok = True

for file in files_to_check:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"  {status} {file}")
    if not exists:
        all_ok = False

if all_ok:
    print("\n✅ Todos los archivos OK - Listo para usar!\n")
else:
    print("\n⚠️  Faltan archivos - revisar la instalación\n")
