#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cmath
import csv
import numpy as np
import cv2
from cv2 import aruco
import socket
import threading
import time

# UDP送信設定
# UDP_IP = "192.168.11.4"
UDP_IP = "192.168.11.6"
# UDP_IP = "172.20.10.4"

# UDP_IP = "127.0.0.1"
UDP_PORT = 50000
POSITION_THRESHOLD= 0.3
ANGLE_THRESHOLD= 30.0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 移動平均フィルタ用のバッファ
WINDOW_SIZE = 5
posX_buffer = []
posY_buffer = []
posZ_buffer = []
rotX_buffer = []
rotY_buffer = []
rotZ_buffer = []

def send_data(data):
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

# 角度を -180°から180°の範囲に正規化
def normalize_angle(angle):
    return (angle + 180) % 360 - 180

# 角度の差分を計算
def angle_difference(angle1, angle2):
    diff = angle1 - angle2
    diff = (diff + 180) % 360 - 180
    return diff

# 角度の移動平均を計算
def deg_mean(angles):
    a = np.deg2rad(angles)
    angles_complex = np.frompyfunc(cmath.exp, 1, 1)(a * 1j)
    mean = cmath.phase(angles_complex.sum()) % (2 * np.pi)
    rounded_mean = round(np.rad2deg(mean), 7)
    return normalize_angle(rounded_mean)

def buffer_append(buffer, new_value):
    buffer.append(new_value)
    if len(buffer) > WINDOW_SIZE:
        buffer.pop(0)

# 移動平均フィルタ
def moving_average(buffer, new_value, angle=False):
    buffer_append(buffer, new_value)
    mean = deg_mean(buffer)if angle else np.mean(buffer)
    return mean

# 閾値フィルタ
def threshold_filter(buffer, mean, new_value, angle=False):
    if len(buffer) < WINDOW_SIZE: return True
    threshold = ANGLE_THRESHOLD if angle else POSITION_THRESHOLD
    diff = abs(angle_difference(mean, new_value)) if angle else abs(mean - new_value)
    print(f"mean: {mean}, new_value: {new_value}, diff: {diff}")
    return diff < threshold

# 閾値フィルタをチェック
def check_thresholds(m_posX, posX, m_posY, posY, m_posZ, posZ,
                     m_rotX, rotX, m_rotY, rotY, m_rotZ, rotZ):
    if not threshold_filter(posX_buffer, m_posX, posX) or \
       not threshold_filter(posY_buffer, m_posY, posY) or \
       not threshold_filter(posZ_buffer, m_posZ, posZ) or \
       not threshold_filter(rotX_buffer, m_rotX, rotX, angle=True) or \
       not threshold_filter(rotY_buffer, m_rotY, rotY, angle=True) or \
       not threshold_filter(rotZ_buffer, m_rotZ, rotZ, angle=True):
        # buffer_append(posX_buffer, posX)
        # buffer_append(posY_buffer, posY)
        # buffer_append(posZ_buffer, posZ)
        # buffer_append(rotX_buffer, rotX)
        # buffer_append(rotY_buffer, rotY)
        # buffer_append(rotZ_buffer, rotZ)
        print("false")
        return False
    return True

def main():
    # CSVファイルの初期化
    data_file = open('data.csv', mode='w', newline='')
    filtered_file = open('filtered_data.csv', mode='w', newline='')

    data_writer = csv.writer(data_file)
    filtered_writer = csv.writer(filtered_file)

    # ヘッダーを書き込む
    data_writer.writerow(['posX', 'posY', 'posZ', 'rotX', 'rotY', 'rotZ'])
    filtered_writer.writerow(['posX', 'posY', 'posZ', 'rotX', 'rotY', 'rotZ'])


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
    
    # フィルタ後の値の初期化
    m_posX = m_posY = m_posZ = None
    m_rotX = m_rotY = m_rotZ = None

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

                # data.csvに出力
                data_writer.writerow([posX, posY, posZ, rotX, rotY, rotZ])
                # 閾値フィルタのチェック関数を呼び出す
                if not check_thresholds(m_posX, posX, m_posY, posY, m_posZ, posZ,m_rotX, rotX, m_rotY, rotY, m_rotZ, rotZ):
                    filtered_writer.writerow([m_posX, m_posY, m_posZ, m_rotX, m_rotY, m_rotZ])
                    continue

                # 移動平均フィルタの適用
                m_posX = moving_average(posX_buffer, posX)
                m_posY = moving_average(posY_buffer, posY)
                m_posZ = moving_average(posZ_buffer, posZ)
                m_rotX = moving_average(rotX_buffer, rotX, angle=True)
                m_rotY = moving_average(rotY_buffer, rotY, angle=True)
                m_rotZ = moving_average(rotZ_buffer, rotZ, angle=True)

                # filtered_data.csvに出力
                filtered_writer.writerow([m_posX, m_posY, m_posZ, m_rotX, m_rotY, m_rotZ])

                # データ送信
                data = f"{m_posX},{m_posY},{m_posZ},{m_rotX},{m_rotY},{m_rotZ}"
                send_data(data)
                print(data)

                # 可視化
                draw_pole_length = marker_length / 2  # 現実での長さ[m]
                cv2.drawFrameAxes(img, camera_matrix, distortion_coeff, rvec, np.array([m_posX, -m_posY, m_posZ]), draw_pole_length)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
