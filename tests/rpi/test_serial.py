import serial
import threading

PORT = '/dev/ttyUSB0'    # Или /dev/ttyACM0, если Arduino через USB
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)

def read_serial():
    while True:
        try:
            line = ser.readline().decode().strip()
            if line:
                print(f"Received: {line}")
        except Exception as e:
            print("Read error:", e)

# Запуск чтения в отдельном потоке
threading.Thread(target=read_serial, daemon=True).start()

print('Type LED_ON or LED_OFF and press Enter to control the LED strip.')
while True:
    cmd = input("> ").strip()
    if cmd:
        ser.write((cmd + "\n").encode())
        print(f"Sent: {cmd}")
