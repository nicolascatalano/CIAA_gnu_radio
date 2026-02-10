#!/usr/bin/env python3
"""
Monitorea el rendimiento del flowgraph GNU Radio
Muestra estadísticas sobre paquetes recibidos vs procesados
"""

import time
import socket
import threading

class UDPMonitor:
    def __init__(self, port=9999):
        self.port = port
        self.packet_count = 0
        self.bytes_received = 0
        self.running = False
        self.start_time = None
        
    def monitor(self):
        """Escucha UDP y cuenta paquetes"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)  # Buffer 1MB
        sock.bind(('0.0.0.0', self.port))
        sock.settimeout(0.1)
        
        print(f"📡 Monitoreando UDP en puerto {self.port}...")
        print(f"   (Inicia GNU Radio en otra terminal)\n")
        
        self.start_time = time.time()
        self.running = True
        
        try:
            while self.running:
                try:
                    data, addr = sock.recvfrom(65536)
                    self.packet_count += 1
                    self.bytes_received += len(data)
                except socket.timeout:
                    continue
                    
        finally:
            sock.close()
    
    def print_stats(self):
        """Imprime estadísticas periódicamente"""
        last_count = 0
        
        while self.running:
            time.sleep(2.0)
            
            if self.packet_count > 0:
                elapsed = time.time() - self.start_time
                pkt_rate = self.packet_count / elapsed
                byte_rate = self.bytes_received / elapsed / 1024 / 1024  # MB/s
                
                pkt_delta = self.packet_count - last_count
                last_count = self.packet_count
                
                print(f"📊 Paquetes: {self.packet_count:6d} | "
                      f"Rate: {pkt_rate:6.1f} pkt/s | "
                      f"Throughput: {byte_rate:5.2f} MB/s | "
                      f"Δ: {pkt_delta:4d} pkt/2s")

if __name__ == '__main__':
    monitor = UDPMonitor(port=9999)
    
    # Thread para estadísticas
    stats_thread = threading.Thread(target=monitor.print_stats, daemon=True)
    stats_thread.start()
    
    # Thread principal monitoreando UDP
    try:
        monitor.monitor()
    except KeyboardInterrupt:
        print(f"\n\n✅ Monitoreo detenido")
        monitor.running = False
        
        if monitor.packet_count > 0:
            elapsed = time.time() - monitor.start_time
            print(f"\n═══ RESUMEN ═══")
            print(f"Total paquetes: {monitor.packet_count}")
            print(f"Total bytes: {monitor.bytes_received / 1024 / 1024:.2f} MB")
            print(f"Duración: {elapsed:.1f} s")
            print(f"Tasa promedio: {monitor.packet_count / elapsed:.1f} pkt/s")
            print(f"Throughput: {monitor.bytes_received / elapsed / 1024 / 1024:.2f} MB/s")
