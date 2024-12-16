#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import aruco
import socket
import time
from scipy.spatial.transform import Rotation as R
from config import UDP_IP, UDP_PORT, CAMERA_MATRIX, DISTORTION_COEFF, MARKER_LENGTH, CAM_HEIGHT, CAM_WIDTH

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data(data):
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

# 角度を 0°から360°の範囲に正規化
def normalize_angle(angle):
    return angle % 360

def main():
    time.sleep(1)
    cap = cv2.VideoCapture(0)
    # 解像度を設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"{actual_width}x{actual_height}")

    # マーカーの辞書選択
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)

    while True:
        data_list = []
        ret, img = cap.read()
        img = cv2.flip(img, -1)

        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)
        aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 255))

        if len(corners) > 0:
            # マーカーごとに処理
            for i, corner in enumerate(corners):
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, MARKER_LENGTH, CAMERA_MATRIX, DISTORTION_COEFF)

                # 不要なaxisを除去
                tvec = np.squeeze(tvec)
                rvec = np.squeeze(rvec)
                posX, posY, posZ = tvec[0], tvec[1], tvec[2]
                rvec[0]=-rvec[0]
                rvec[2]=-rvec[2]
                # 回転ベクトル -> Rotationクラスのrotationオブジェクト
                rotation = R.from_rotvec(rvec)
                # Rotationクラスのrotationオブジェクト -> クォータニオン
                quaternion = rotation.as_quat()
                data = f"{ids[i][0]},{posX},{posY},{posZ},{quaternion[0]},{quaternion[1]},{quaternion[2]},{quaternion[3]}"
                data_list.append(data)

                # 可視化
                draw_pole_length = MARKER_LENGTH / 2
                cv2.drawFrameAxes(img, CAMERA_MATRIX, DISTORTION_COEFF, rvec, tvec, draw_pole_length)


        if(data_list):
            combined_data = ";".join(data_list)
            send_data(combined_data)
            print(combined_data)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
