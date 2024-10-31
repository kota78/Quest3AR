#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import aruco
import socket
import threading
import time

# UDP送信設定
UDP_IP = "192.168.11.4"
UDP_PORT = 50000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data(data):
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

# 指数移動平均フィルタのクラス
class ExponentialMovingAverage:
    def __init__(self, alpha=0.5):
        """
        alpha: 平滑化の係数 (0 < alpha < 1)
        alphaが小さいほど平滑化が強くなる
        """
        self.alpha = alpha
        self.ema_value = None

    def apply(self, current_value):
        if self.ema_value is None:
            self.ema_value = current_value
        else:
            self.ema_value = self.alpha * current_value + (1 - self.alpha) * self.ema_value
        return self.ema_value

def save_data(file_name, data):
    with open(file_name, 'a') as f:
        f.write(data + '\n')

def main():
    cap = cv2.VideoCapture(0)
    # マーカーサイズ
    marker_length = 0.056 # [m]
    # マーカーの辞書選択
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
    # 小型カメラの内部パラメータ
    camera_matrix = np.array([[464.76830292, 0, 512.35210634],
                              [0, 469.61837529, 385.2203724],
                              [0, 0, 1]])
    distortion_coeff = np.array([-0.3136963, 0.10256045, -0.01269226, 0.00985827, -0.01445209])

    # 各軸に対して指数移動平均フィルタを適用 (座標と回転)
    ema_posX = ExponentialMovingAverage(alpha=0.3)
    ema_posY = ExponentialMovingAverage(alpha=0.3)
    ema_posZ = ExponentialMovingAverage(alpha=0.3)
    ema_rotX = ExponentialMovingAverage(alpha=0.3)
    ema_rotY = ExponentialMovingAverage(alpha=0.3)
    ema_rotZ = ExponentialMovingAverage(alpha=0.3)

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

                # フィルタ適用前の値
                raw_posX, raw_posY, raw_posZ = tvec[0], -tvec[1], tvec[2]  # Y座標を反転
                raw_rotX, raw_rotY, raw_rotZ = -euler_angle[0, 0], euler_angle[1, 0], euler_angle[2, 0]  # ロール軸を反転

                # フィルタ適用前のデータを保存
                raw_data = f"{raw_posX},{raw_posY},{raw_posZ},{raw_rotX},{raw_rotY},{raw_rotZ}"
                save_data('raw_data.txt', raw_data)

                # 指数移動平均フィルタを適用
                posX = ema_posX.apply(raw_posX)
                posY = ema_posY.apply(raw_posY)
                posZ = ema_posZ.apply(raw_posZ)
                rotX = ema_rotX.apply(raw_rotX)
                rotY = ema_rotY.apply(raw_rotY)
                rotZ = ema_rotZ.apply(raw_rotZ)

                # フィルタ適用後のデータを保存
                filtered_data = f"{posX},{posY},{posZ},{rotX},{rotY},{rotZ}"
                save_data('filtered_data.txt', filtered_data)

                print(f"Filtered -> x: {posX}, y: {posY}, z: {posZ}, roll: {rotX}, pitch: {rotY}, yaw: {rotZ}")

                # データ送信
                send_data(filtered_data)

                # 可視化
                draw_pole_length = marker_length / 2  # 現実での長さ[m]
                cv2.drawFrameAxes(img, camera_matrix, distortion_coeff, rvec, tvec, draw_pole_length)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
