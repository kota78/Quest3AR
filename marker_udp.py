#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import aruco
import socket
import threading
import time
from config import UDP_IP, UDP_PORT, CAMERA_MATRIX, DISTORTION_COEFF, MARKER_LENGTH

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data(data):
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

# 角度を -180°から180°の範囲に正規化
def normalize_angle(angle):
    return (angle + 180) % 360 - 180

def main():
    cap = cv2.VideoCapture(0)
   
    # マーカーの辞書選択
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)

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
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, MARKER_LENGTH, CAMERA_MATRIX, DISTORTION_COEFF)

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
                rotX, rotY, rotZ = normalize_angle(euler_angle[0, 0])*-1, normalize_angle(euler_angle[1, 0]), normalize_angle(euler_angle[2, 0])  # ロール軸を反転

                print(f"x: {posX}, y: {posY}, z: {posZ}, roll: {rotX}, pitch: {rotY}, yaw: {rotZ}")

                # データ送信
                data = f"{posX},{posY},{posZ},{rotX},{rotY},{rotZ}"
                send_data(data)
                print(data)

                # 可視化
                draw_pole_length = MARKER_LENGTH / 2  # 現実での長さ[m]
                cv2.drawFrameAxes(img, CAMERA_MATRIX, DISTORTION_COEFF, rvec, tvec, draw_pole_length)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
