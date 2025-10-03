import serial

# Configuração da porta serial
SERIAL_PORT = "/dev/ttyUSB0"  # Mesma porta usada no simulador
BAUDRATE = 9600

# Inicialização da porta serial
ser = serial.Serial(SERIAL_PORT, BAUDRATE)

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip()
            heave, pitch, roll = map(float, data.split(","))
            print(f"Recebido - Heave: {heave}m, Pitch: {pitch}°, Roll: {roll}°")
except KeyboardInterrupt:
    print("Encerrando...")
    ser.close()
