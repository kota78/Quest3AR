import socket
import threading
import time
from config import UDP_IP, UDP_PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 初期座標と角度
posX, posY, posZ = 0.0, 0.0, 1.0
rotX, rotY, rotZ = 0.0, 0.0, 0.0

def send_data():
    global posX, posY, posZ, rotX, rotY, rotZ
    while True:
        data = f"{posX},{posY},{posZ},{rotX},{rotY},{rotZ}"
        sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))
        time.sleep(0.1)  # 送信間隔

def update_rotation():
    global rotX, rotY, rotZ
    axis = 0  # 0: rotX, 1: rotY, 2: rotZ
    while True:
        if axis == 0:
            rotX += 10.0
            if rotX % 90 == 0:
                axis = 1
        elif axis == 1:
            rotY += 10.0
            if rotY % 90 == 0:
                axis = 2
        elif axis == 2:
            rotZ += 10.0
            if(rotZ == 360):
                break
            if rotZ % 90 == 0:
                axis = 0
        print(f"Updated Rotation: ({rotX}, {rotY}, {rotZ})")
        time.sleep(0.2)  # 0.5秒ごとに変更

# スレッドを使ってデータ送信と自動回転を並行して行う
send_thread = threading.Thread(target=send_data)
rotation_thread = threading.Thread(target=update_rotation)

send_thread.start()
rotation_thread.start()

send_thread.join()
rotation_thread.join()
