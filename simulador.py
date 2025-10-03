import random
import time
import serial

# Configuração da porta serial simulada
SERIAL_PORT = "/dev/ttyUSB0"  # Mude para a porta correspondente no seu sistema
BAUDRATE = 9600

# Inicialização da porta serial
ser = serial.Serial(SERIAL_PORT, BAUDRATE)

def generate_data():
    # Simula dados de heave, pitch e roll
    heave = round(random.uniform(-10, 10), 2)  # Metros
    pitch = round(random.uniform(-20, 20), 2) # Graus
    roll = round(random.uniform(-20, 20), 2)  # Graus
    return heave, pitch, roll

try:
    while True:
        heave, pitch, roll = generate_data()
        data = f"{heave},{pitch},{roll}\n"
        ser.write(data.encode())  # Envia os dados via serial
        print(f"Enviado: {data.strip()}")
        time.sleep(0.5)  # Taxa de atualização
except KeyboardInterrupt:
    print("Encerrando...")
    ser.close()


