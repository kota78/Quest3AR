import socket
import threading
import time

UDP_IP = "127.0.0.1"
# UDP_IP = "192.168.11.30"
UDP_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 初期座標と角度
posX, posY, posZ = 0.0, 0.0, 0.0
rotX, rotY, rotZ = 0.0, 0.0, 0.0

def send_data():
    global posX, posY, posZ, rotX, rotY, rotZ
    while True:
        data = f"{posX},{posY},{posZ},{rotX},{rotY},{rotZ}"
        sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))
        time.sleep(0.1)  # 送信間隔

def update_position():
    global posX, posY, posZ, rotX, rotY, rotZ
    while True:
        command = input("Enter command (w/a/s/d/q/e for position, i/j/k/l/u/o for rotation): ").strip()
        if command == 'w':
            posY += 1.0
        elif command == 's':
            posY -= 1.0
        elif command == 'a':
            posX -= 1.0
        elif command == 'd':
            posX += 1.0
        elif command == 'q':
            posZ += 1.0
        elif command == 'e':
            posZ -= 1.0
        elif command == 'i':
            rotX += 5.0
        elif command == 'k':
            rotX -= 5.0
        elif command == 'j':
            rotY -= 5.0
        elif command == 'l':
            rotY += 5.0
        elif command == 'u':
            rotZ += 5.0
        elif command == 'o':
            rotZ -= 5.0
        print(f"Updated Position: ({posX}, {posY}, {posZ}) Rotation: ({rotX}, {rotY}, {rotZ})")

# スレッドを使ってデータ送信とキーボード入力を並行して行う
send_thread = threading.Thread(target=send_data)
input_thread = threading.Thread(target=update_position)

send_thread.start()
input_thread.start()

send_thread.join()
input_thread.join()
