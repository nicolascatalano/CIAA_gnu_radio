#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO - Por qué los gráficos se ven mal
"""

print("="*70)
print("🔍 DIAGNÓSTICO DE PROBLEMA")
print("="*70)

print("""
SÍNTOMAS REPORTADOS:
-------------------
✅ Unpacker inició correctamente
✅ Mensajes de estadísticas aparecen
✅ Drop rate: 0.00%
❌ Buffer decrece: 1430 → 1100 bytes (se agota)
❌ Se detuvo después de ~81500 paquetes
❌ Gráficos muestran datos "mezclados"

ANÁLISIS:
---------

1. BUFFER DECRECIENTE (1430 → 1100 bytes):
   
   Causa: El flujo de datos UDP SE DETUVO
   
   ¿Por qué?
   a) La CIAA dejó de transmitir
   b) Se agotó la memoria del servidor en la CIAA
   c) El programa sist_adq_crc.elf terminó
   d) Problema de red (desconexión)
   
   Solución:
   → Verificar en la CIAA si el proceso sigue corriendo
   → Reiniciar streaming: ./sist_adq_crc.elf client_config


2. GRÁFICOS CON DATOS "MEZCLADOS":
   
   Observación: Pulsos entre -20000 y +20000, no patrón limpio
   
   Posibles causas:
   a) Python CACHEÓ el módulo viejo (con offset 88)
   b) Los datos NO son patrón contador (son ADC real)
   c) La CIAA está en modo ADC, no en modo contador
   
   Solución aplicada:
   ✅ Cache de Python eliminado (__pycache__)
   
   Próximo paso:
   → CERRAR completamente GNU Radio
   → Volver a ejecutar
   → Verificar que cargue el módulo correcto


3. CONFIGURACIÓN DE LA CIAA:
   
   Para ver patrón CONTADOR limpio, la CIAA debe estar en:
   
   DEBUG_Control = 0xF (CONT_NBITS)
   DATA_Source_Mux = 0x2 (CONTADOR)
   FIFO_Input_Mux = 0x4 (MUX_DATA)
   
   Verificar con:
   ./axi_rw_test.elf r 43c00080  # DEBUG_Control
   ./axi_rw_test.elf r 43c30008  # DATA_Source_Mux
   ./axi_rw_test.elf r 43c30004  # FIFO_Input_Mux
   
   Si NO están en modo contador, los gráficos mostrarán
   señales ADC (que pueden parecer "mezcladas" si no hay
   señal de entrada conectada).


PASOS PARA RESOLVER:
====================

PASO 1: LIMPIAR Y REEJECUTAR (YA HECHO)
---------------------------------------
✅ Cache eliminado
→ Cerrar GNU Radio COMPLETAMENTE
→ Volver a abrir CIAA_UDP_Receiver_Working.grc
→ Ejecutar (▶️)


PASO 2: VERIFICAR CONFIGURACIÓN CIAA
------------------------------------
Conectar por SSH a la CIAA:

$ ssh root@192.168.0.22

Verificar registros:
$ cd /mnt/currentVersions
$ ./axi_rw_test.elf r 43c00080
   → Debe leer: 0x0000000F (modo contador)
   
$ ./axi_rw_test.elf r 43c30008
   → Debe leer: 0x00000002 (fuente contador)

$ ./axi_rw_test.elf r 43c30004
   → Debe leer: 0x00000004 (FIFO desde MUX)

Si NO están así, configurar:
$ ./axi_rw_test.elf w 43c00080 f
$ ./axi_rw_test.elf w 43c30008 2
$ ./axi_rw_test.elf w 43c30004 4


PASO 3: REINICIAR STREAMING
---------------------------
Detener proceso actual (Ctrl+C si está corriendo)

Configurar destino (reemplazar con tu IP):
$ echo "192.168.0.100 9999 100000" > client_config

Iniciar:
$ ./sist_adq_crc.elf client_config


PASO 4: EJECUTAR GNU RADIO
--------------------------
En tu PC:
> gnuradio-companion CIAA_UDP_Receiver_Working.grc
> Click Run (▶️)


QUÉ DEBERÍAS VER:
=================

CON MODO CONTADOR:
-----------------
Gráfico temporal:
  ┌─────┐
  │    /│  ← Rampa ascendente continua
  │   / │     (incrementa +1 cada sample)
  │  /  │
  │ /   │
  └─────┘

Consola:
  [Unpacker] Packets: 500, Buffer: 0-100 bytes, Drop rate: 0.00%
  (Buffer debería mantenerse cerca de 0)


CON MODO ADC (sin señal):
------------------------
Gráfico temporal:
  ┌─────┐
  │ ||| │  ← Ruido/señales variables
  │|   |│     (valores pequeños si no hay señal)
  │ | | │
  │  |  │
  └─────┘

Esto es NORMAL si no hay señal analógica conectada.


SI SIGUE MAL:
=============

1. Captura datos para análisis:
   En GNU Radio, los file sinks están deshabilitados.
   Habilitar temporalmente para guardar datos:
   - Editar .grc
   - blocks_file_sink_0: state: disabled → enabled
   - Ejecutar 10 segundos
   - Analizar archivo ciaa_udp_dump.bin

2. Usa el script de validación:
   > python test_parser_fix.py
   
   Debería mostrar patrón contador si la CIAA está en modo contador.

""")

print("="*70)
print("✅ SIGUIENTE ACCIÓN REQUERIDA:")
print("="*70)
print("""
1. CERRAR GNU Radio Companion completamente
2. Verificar configuración en la CIAA (SSH)
3. Reiniciar streaming en la CIAA
4. Volver a ejecutar el flowgraph
5. Observar si los gráficos mejoran
""")
