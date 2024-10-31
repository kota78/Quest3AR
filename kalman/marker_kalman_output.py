#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import aruco
import socket
import time

# UDP送信設定
UDP_IP = "192.168.11.4"
UDP_PORT = 50000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# カルマンフィルターの初期設定
def init_kalman():
    kf = cv2.KalmanFilter(6, 6)
    kf.measurementMatrix = np.eye(6, dtype=np.float32)
    kf.transitionMatrix = np.eye(6, dtype=np.float32)
    kf.processNoiseCov = np.eye(6, dtype=np.float32) * 1e-5
    kf.measurementNoiseCov = np.eye(6, dtype=np.float32) * 1e-3
    kf.errorCovPost = np.eye(6, dtype=np.float32)
    return kf

kalman = init_kalman()

# 異常値検出の閾値
THRESHOLD = 0.5  # 変化が大きすぎる場合に異常値と見なす

def is_anomalous(new_value, previous_value):
    return np.abs(new_value - previous_value) > THRESHOLD

def send_data(data):
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

def main():
    cap = cv2.VideoCapture(0)
    marker_length = 0.056  # [m]
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)

    camera_matrix = np.array([[464.76830292, 0, 512.35210634],
                              [0, 469.61837529, 385.2203724],
                              [0, 0, 1]])
    distortion_coeff = np.array([-0.3136963, 0.10256045, -0.01269226, 0.00985827, -0.01445209])

    # ファイルの準備
    raw_file = open("raw_data.txt", "w")
    filtered_file = open("filtered_data.txt", "w")

    # 初期状態の設定
    previous_data = np.zeros(6)

    while True:
        ret, img = cap.read()
        img = cv2.flip(img, -1)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)
        aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 255))

        if len(corners) > 0:
            for i, corner in enumerate(corners):
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, marker_length, camera_matrix, distortion_coeff)

                tvec = np.squeeze(tvec)
                rvec = np.squeeze(rvec)
                rvec_matrix = cv2.Rodrigues(rvec)[0]
                transpose_tvec = tvec[np.newaxis, :].T
                proj_matrix = np.hstack((rvec_matrix, transpose_tvec))
                euler_angle = cv2.decomposeProjectionMatrix(proj_matrix)[6]

                posX, posY, posZ = tvec[0], -tvec[1], tvec[2]
                rotX, rotY, rotZ = -euler_angle[0, 0], euler_angle[1, 0], euler_angle[2, 0]

                # 観測値を設定
                measurement = np.array([posX, posY, posZ, rotX, rotY, rotZ], dtype=np.float32)

                # カルマンフィルターで予測と更新
                kalman.correct(measurement)
                predicted = kalman.predict()

                # 異常値検出
                if not np.any(is_anomalous(predicted, previous_data)):
                    previous_data = predicted
                else:
                    print("Anomalous data detected, skipping update.")

                # データをファイルに書き込む（生データとフィルタ後のデータ）
                raw_data_str = f"{posX},{posY},{posZ},{rotX},{rotY},{rotZ}\n"
                filtered_data_str = f"{predicted[0]},{predicted[1]},{predicted[2]},{predicted[3]},{predicted[4]},{predicted[5]}\n"
                
                raw_file.write(raw_data_str)
                filtered_file.write(filtered_data_str)

                # データ送信
                send_data(filtered_data_str)
                print(filtered_data_str)

                draw_pole_length = marker_length / 2
                cv2.drawFrameAxes(img, camera_matrix, distortion_coeff, rvec, tvec, draw_pole_length)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # ファイルを閉じる
    raw_file.close()
    filtered_file.close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
