import socket
import threading
import time
from config import UDP_IP, UDP_PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
POSITION_VALUE=0.5
ROTAION_VALUE=30.0

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
            posY += POSITION_VALUE
        elif command == 's':
            posY -= POSITION_VALUE
        elif command == 'a':
            posX -= POSITION_VALUE
        elif command == 'd':
            posX += POSITION_VALUE
        elif command == 'q':
            posZ += POSITION_VALUE
        elif command == 'e':
            posZ -= POSITION_VALUE
        elif command == 'i':
            rotX += ROTAION_VALUE
        elif command == 'k':
            rotX -= ROTAION_VALUE
        elif command == 'j':
            rotY -= ROTAION_VALUE
        elif command == 'l':
            rotY += ROTAION_VALUE
        elif command == 'u':
            rotZ += ROTAION_VALUE
        elif command == 'o':
            rotZ -= ROTAION_VALUE
        print(f"Updated Position: ({posX}, {posY}, {posZ}) Rotation: ({rotX}, {rotY}, {rotZ})")

# スレッドを使ってデータ送信とキーボード入力を並行して行う
send_thread = threading.Thread(target=send_data)
input_thread = threading.Thread(target=update_position)

send_thread.start()
input_thread.start()

send_thread.join()
input_thread.join()
