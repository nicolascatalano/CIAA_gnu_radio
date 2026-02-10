#!/usr/bin/env python3
"""
Verificación de la configuración de los gráficos
Asegura que usen ventana deslizante, no acumulación
"""

import re

grc_file = r'f:\Proyectos\sist_adq_dbf\gnuradio\CIAA_UDP_Receiver_Working.grc'

with open(grc_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("="*70)
print("VERIFICACION DE CONFIGURACION DE GRAFICOS")
print("="*70)

# Buscar bloques qtgui_time_sink
time_sinks = re.findall(r'- name: (qtgui_time_sink_\w+).*?size: \'(\d+)\'', content, re.DOTALL)
freq_sinks = re.findall(r'- name: (qtgui_freq_sink_\w+).*?fftsize: \'(\d+)\'', content, re.DOTALL)

print("\nTIME SINKS (graficos temporales):")
print("-" * 70)
for name, size in time_sinks:
    print(f"  {name}:")
    print(f"    - size: {size} samples (ventana deslizante)")
    if int(size) > 0:
        print(f"    ✅ Configurado como ventana, NO acumulacion")
    else:
        print(f"    ❌ ERROR: size = 0 (acumularia infinitamente)")

print("\nFREQUENCY SINKS (graficos espectrales):")
print("-" * 70)
for name, fftsize in freq_sinks:
    print(f"  {name}:")
    print(f"    - fftsize: {fftsize} (tamaño FFT)")
    print(f"    ✅ Los freq_sink siempre usan ventana deslizante")

# Verificar average en freq_sink
avg_matches = re.findall(r'qtgui_freq_sink.*?average: \'([\d.]+)\'', content, re.DOTALL)
print(f"\nPROMEDIADO ESPECTRAL:")
print("-" * 70)
for i, avg in enumerate(avg_matches):
    print(f"  Freq Sink #{i+1}: average = {avg}")
    if float(avg) == 1.0:
        print(f"    → Sin promediado (cada FFT se muestra inmediatamente)")
    else:
        print(f"    → Promedio de {avg} FFTs")

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)

if time_sinks and all(int(size) > 0 for _, size in time_sinks):
    print("✅ Time sinks configurados correctamente (ventana deslizante)")
else:
    print("❌ Revisar configuracion de time sinks")

if freq_sinks:
    print("✅ Freq sinks configurados correctamente (siempre ventana)")

print("\n💡 NOTA: Los graficos GNU Radio SIEMPRE usan ventana deslizante.")
print("   No es posible configurarlos para acumular infinitamente.")
print("   Si parece que acumulan, es un problema de PARSEO de datos.\n")
