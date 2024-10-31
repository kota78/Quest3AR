#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import aruco
import socket
import threading
import time

# UDP送信設定
# UDP_IP = "192.168.11.4"
UDP_IP = "192.168.11.30"
# UDP_IP = "172.20.10.4"

# UDP_IP = "127.0.0.1"
UDP_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data(data):
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

def main():
    cap = cv2.VideoCapture(0)
    # マーカーサイズ
    marker_length = 0.056 # [m]
    # マーカーの辞書選択
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
    
    # 自前Webカメラの内部パラメータ
    # camera_matrix = np.array([[1.33168655e+03,0.00000000e+00,9.54841857e+02],
    #                           [0.00000000e+00,1.33162266e+03,5.60401382e+02],
    #                           [0.00000000e+00,0.00000000e+00,1.00000000e+00]])
    # distortion_coeff = np.array([-0.35524981,0.01349514,-0.00471847,0.00897172,0.13142206])
    
    # 小型カメラの内部パラメータ
    camera_matrix = np.array([[464.76830292,0,512.35210634],
                              [0,469.61837529,385.2203724],
                              [0, 0, 1]])
    distortion_coeff = np.array([-0.3136963, 0.10256045, -0.01269226, 0.00985827, -0.01445209])

    while True:
        ret, img = cap.read()
        img = cv2.flip(img, -1)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)
        # 可視化
        aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 255))

        if len(corners) > 0:
            # マーカーごとに処理
            for i, corner in enumerate(corners):
                # rvec -> rotation vector, tvec -> translation vector
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, marker_length, camera_matrix, distortion_coeff)

                # < rodoriguesからeuluerへの変換 >

                # 不要なaxisを除去
                tvec = np.squeeze(tvec)
                rvec = np.squeeze(rvec)
                # 回転ベクトルからrodoriguesへ変換
                rvec_matrix = cv2.Rodrigues(rvec)
                rvec_matrix = rvec_matrix[0]  # rodoriguesから抜き出し
                # 並進ベクトルの転置
                transpose_tvec = tvec[np.newaxis, :].T
                # 合成
                proj_matrix = np.hstack((rvec_matrix, transpose_tvec))
                # オイラー角への変換
                euler_angle = cv2.decomposeProjectionMatrix(proj_matrix)[6]  # [deg]

                posX, posY, posZ = tvec[0], -tvec[1], tvec[2]  # Y座標を反転
                rotX, rotY, rotZ = -euler_angle[0, 0], euler_angle[1, 0], euler_angle[2, 0]  # ロール軸を反転

                print(f"x: {posX}, y: {posY}, z: {posZ}, roll: {rotX}, pitch: {rotY}, yaw: {rotZ}")

                # データ送信
                data = f"{posX},{posY},{posZ},{rotX},{rotY},{rotZ}"
                send_data(data)
                print(data)

                # 可視化
                draw_pole_length = marker_length / 2  # 現実での長さ[m]
                cv2.drawFrameAxes(img, camera_matrix, distortion_coeff, rvec, tvec, draw_pole_length)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
