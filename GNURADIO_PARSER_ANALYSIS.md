# Análisis del Flowgraph GNU Radio - CIAA UDP Parser
**Fecha**: 3 de Febrero, 2026  
**Ubicación**: `f:\Proyectos\sist_adq_dbf\gnuradio\`

---

## 🔍 RESUMEN EJECUTIVO

**ESTADO ACTUAL**: El formato valido actual tiene el header en offset 0 y el payload a continuacion (offset 88), sin CRC. El flujo funciona con parseo por PDU.

**Impacto**: Los datos graficados NO corresponden a las muestras reales del ADC si se usan offsets incorrectos.

---

## 📋 ARCHIVOS ANALIZADOS

### Flowgraphs Principales
1. **`CIAA_UDP_Receiver_Working.grc`** + `CIAA_UDP_Receiver_Working_epy_block_ciaa_unpacker.py`
2. **`CIAA_GUI.grc`** + `CIAA_GUI_epy_block_unpacker.py`
3. **`CIAA.grc`** + `CIAA_epy_block_0.py`

### Módulos de Parseo
- **`gnuradio_streaming/packet_parser.py`** - Clase `CIAAPacketParser` (importada por algunos bloques)
- **Bloques embebidos** - Parseo directo en los archivos `_epy_block_*.py`

---

## 🐛 ERRORES DETECTADOS (HISTORICOS)

### 1. **Estructura de Paquete INCORRECTA**

#### ❌ Lo que se usaba ANTES:
```
┌──────────────────────────────────────────────────────────┐
│ HEADER (88 bytes) │ PAYLOAD (1344 bytes) │ CRC (4 bytes) │
│ offset 0-87       │ offset 88-1431       │ offset 1432   │
└──────────────────────────────────────────────────────────┘
```

**Código erróneo en `packet_parser.py` línea 45-110:**
```python
def parse_header(self, data):
    """
    Parsea header de 88 bytes
    """
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Header incompleto: {len(data)} < {HEADER_SIZE}")
    
    header = {}
    offset = 0  # ❌ EMPIEZA EN OFFSET 0!
    
    # Timestamps
    header['timestamp_sec'] = struct.unpack_from('<Q', data, offset)[0]
    # ... resto del parseo desde offset 0
```

**Código erróneo en `CIAA_UDP_Receiver_Working_epy_block_ciaa_unpacker.py` línea 105:**
```python
def _simple_unpack(self, packet_bytes):
    """Unpack CIAA packet (1432 bytes)"""
    if len(packet_bytes) != 1432:
        raise ValueError(f"Invalid packet size: {len(packet_bytes)}")
    
    # Extract payload (skip 88-byte header)
    payload = packet_bytes[88:88+1344]  # ❌ ASUME HEADER EN offset 0!
```

**Código erróneo en `CIAA_GUI_epy_block_unpacker.py` línea 40:**
```python
payload_start = PACKET_HEADER_SIZE  # = 88
# ...
for row in range(SAMPLES_PER_PACKET):
    for ch in range(NUM_CHANNELS):
        offset = payload_start + (row * NUM_CHANNELS * 4) + (ch * 4)
        # ❌ LEE DESDE offset 88, que contiene parte del PAYLOAD!
```

---

#### ✅ Estructura REAL (formato valido actual):
```
┌──────────────────────────────────────────────────────────┐
│ HEADER (88 bytes) │ PAYLOAD (1344 bytes)                │
│ offset 0-87       │ offset 88-1431                      │
└──────────────────────────────────────────────────────────┘
```

**Total**: 1432 bytes

**Razón del error**: El parser estaba alineado al bug del puntero UDP. Con el fix, el formato valido es header al inicio.

---

### 2. **Campo CRC**

El formato valido actual **no incluye CRC**. Cualquier lectura de 4 bytes adicionales debe eliminarse.

---

### 3. **Búsqueda de Sync Incorrecta**

`CIAA_UDP_Receiver_Working_epy_block_ciaa_unpacker.py` línea 31-43 intenta encontrar el inicio del paquete buscando `payload_size == 1344`:

```python
def _find_packet_sync(self, buffer):
    """Find packet boundary by looking for valid payload_size field"""
    for offset in range(min(10000, len(buffer) - 88)):
        if offset + 86 <= len(buffer):
            try:
                payload_size = struct.unpack('<H', buffer[offset+84:offset+86])[0]
                if payload_size == 1344:  # ❌ Busca en offset+84 relativo al inicio
                    return offset
```

**Problema**: El campo `payload_size` esta en `offset 85` dentro del header (valor 84), y el header comienza en el byte 0 del paquete. Esto ya no aplica si se parsea por PDU.

---

## 📊 COMPARACIÓN: PARSEO CORRECTO vs INCORRECTO

### Ejemplo con Paquete Real

Supongamos un paquete UDP de 1432 bytes:

#### Parseo INCORRECTO (actual):
```python
# Lee "header" desde offset 0-87 (en realidad es PAYLOAD!)
timestamp_sec = struct.unpack('<Q', packet[0:8])[0]  # ❌ Lee primeros 8 bytes del payload

# Lee "payload" desde offset 88-1431 (mezcla de payload real + parte del header)
payload = packet[88:88+1344]  # ❌ Contiene últimos 1256 bytes de payload + primeros 88 bytes del header real
```

#### Parseo CORRECTO (formato valido actual):
```python
# Leer HEADER desde offset 0-87
timestamp_sec = struct.unpack('<Q', packet[0:8])[0]
timestamp_nsec = struct.unpack('<Q', packet[8:16])[0]

# Leer PAYLOAD desde offset 88-1431
payload = packet[88:88+1344]
```

---

## 🔧 ARCHIVOS QUE NECESITAN CORRECCIÓN

### Prioridad ALTA (usados activamente):

1. **`gnuradio_streaming/packet_parser.py`**
   - Clase `CIAAPacketParser`
   - Métodos `parse_header()` y `parse_payload()` líneas 45-155
    - Constante `HEADER_OFFSET` debe ser `0`

2. **`gnuradio/CIAA_UDP_Receiver_Working_epy_block_ciaa_unpacker.py`**
   - Método `_simple_unpack()` línea 105
   - Método `_find_packet_sync()` línea 31

3. **`gnuradio/CIAA_GUI_epy_block_unpacker.py`**
    - Constante `PACKET_HEADER_SIZE` linea 7 (payload_start = 88)
   - Loop de parseo líneas 40-53

### Prioridad MEDIA (posiblemente obsoletos):

4. **`gnuradio/CIAA_epy_block_0.py`** - Verificar si está en uso
5. **`gnuradio/CIAA_GUI_epy_block_ciaa_apply.py`** - Si hace parseo directo

---

## ✅ REFERENCIA CORRECTA

El archivo **`udp_receiver_parser.py`** (en la raíz del proyecto) **SÍ tiene el parseo correcto**:

```python
# Línea 58-60
HEADER_OFFSET = 0           # Header starts at packet beginning
PAYLOAD_SIZE = 1344         # Payload size (21 samples × 16 ch × 4 bytes)
CRC_SIZE = 0                # No CRC in current packets
```

**Este debe ser el modelo para corregir los bloques GNU Radio.**

---

## 🎯 CONSECUENCIAS DEL ERROR ACTUAL

1. **Datos graficados incorrectos**: Las señales mostradas en GNU Radio NO son las muestras reales del ADC
2. **Timestamps inválidos**: Los timestamps parseados son basura (primeros 16 bytes del payload)
3. **FIFO flags ilegibles**: No se puede detectar overflow/underflow correctamente
4. **Sincronización de paquetes falla**: El algoritmo de búsqueda de sync no funciona

---

## 📝 PLAN DE CORRECCIÓN PROPUESTO

### Opción A: Modificar módulos existentes (RECOMENDADO)
1. Corregir `packet_parser.py` con estructura real
2. Actualizar bloques embebidos GNU Radio
3. Probar con captura UDP conocida (ej. `ciaa_udp_dump.bin`)

### Opción B: Reemplazar con parser verificado
1. Copiar lógica de `udp_receiver_parser.py` a `packet_parser.py`
2. Adaptar para GNU Radio (mantener interfaz de clase)
3. Probar con flowgraph existente

---

## ❓ PREGUNTAS PARA EL USUARIO

1. **¿Cuál flowgraph es el que usás actualmente?**
   - `CIAA_UDP_Receiver_Working.grc`
   - `CIAA_GUI.grc`
   - Otro?

2. **¿Preferís que corrija los archivos existentes o cree versiones nuevas "_fixed"?**

3. **¿Tenés capturas UDP recientes para validar el fix?** (ej. archivos `.bin` con datos de prueba)

4. **¿Los flowgraphs tienen que funcionar con datos en tiempo real (UDP streaming) o también con archivos grabados?**

---

## 🔗 REFERENCIAS

- **Documentación oficial**: `.github/copilot-instructions.md` sección "UDP Packet Structure"
- **Parser correcto**: `udp_receiver_parser.py` líneas 1-100
- **Test de validación**: `test_header_parse_fix.py` (valida offsets correctos)
- **Issue reportado**: Documentado en `UDP_PARSER_FIX_SUMMARY.md`

---

## 📌 CONCLUSIÓN

Los flowgraphs de GNU Radio tienen un error arquitectonico en el parseo de paquetes UDP que impide visualizar correctamente los datos del ADC. La correccion requiere modificar 3-4 archivos Python para leer el header desde el offset 0 en lugar del offset 1348.

**Severidad**: CRÍTICA  
**Complejidad del fix**: BAJA (cambiar offsets y reordenar lectura)  
**Tiempo estimado**: 30-45 minutos + testing

