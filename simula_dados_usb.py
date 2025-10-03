# imulador para testes (sem dispositivo USB real)
# Se quiser simular dados chegando por USB, use um script em paralelo como esse:

# Enviar dados para porta serial simulada (apenas para testes)
import serial
import time
import numpy as np

ser = serial.Serial('/dev/ttyUSB0', 9600)

t = 0
while True:
    heave = np.sin(2 * np.pi * 0.25 * t) * (1 + 0.5 * np.sin(2 * np.pi * 0.01 * t))
    ser.write(f"{heave:.3f}\n".encode())
    time.sleep(1)
    t += 1

    