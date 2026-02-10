"""Script para detectar puerto COM del Arduino"""
import serial.tools.list_ports

print("🔍 Detectando puertos COM disponibles...\n")

ports = serial.tools.list_ports.comports()

if not ports:
    print("❌ No se encontraron puertos COM")
else:
    print(f"✅ Se encontraron {len(ports)} puerto(s):\n")
    for port in ports:
        print(f"Puerto: {port.device}")
        print(f"  Descripción: {port.description}")
        print(f"  Hardware ID: {port.hwid}")
        
        # Detectar si es Arduino
        if 'Arduino' in port.description or 'CH340' in port.description or 'USB' in port.description:
            print(f"  ⭐ POSIBLE ARDUINO DETECTADO")
        print()
    
    print("\n📝 Actualiza controller/config.py con el puerto correcto")
    print(f"   SERIAL_PORT = '{ports[0].device}'")
