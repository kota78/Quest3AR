#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import numpy as np
import cv2
from cv2 import aruco
import socket
from config import UDP_IP, UDP_PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data(data):
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

# 閾値フィルタのクラス
class ThresholdFilter:
    def __init__(self, position_threshold=0.3, angle_threshold=30.0):
        self.prev_data = None
        self.position_threshold = position_threshold  # 位置の変化量の閾値
        self.angle_threshold = angle_threshold  # 角度の変化量の閾値

    def apply(self, new_data):
        # 初回のデータはそのまま使用
        if self.prev_data is None:
            self.prev_data = new_data
            return new_data

        # 位置の差分を計算
        position_diff = np.abs(new_data[:3] - self.prev_data[:3])
        # 角度の差分を計算
        angle_diff = np.abs(new_data[3:] - self.prev_data[3:])
        # ラップアラウンドを処理
        angle_diff = np.minimum(angle_diff, 360 - angle_diff)

        print(f"pos_diff: {position_diff}, angle_diff: {angle_diff}")

        # 位置の差分が位置の閾値を超えているか、角度の差分が角度の閾値を超えているかを確認
        if np.any(position_diff > self.position_threshold) or np.any(angle_diff > self.angle_threshold):
            return self.prev_data

        # 位置も角度も閾値以下であれば、データを更新して返す
        self.prev_data = new_data
        return new_data

def main():
     # CSVファイルの初期化
    data_file = open('data.csv', mode='w', newline='')
    filtered_file = open('filtered_data.csv', mode='w', newline='')

    data_writer = csv.writer(data_file)
    filtered_writer = csv.writer(filtered_file)
    
    # ヘッダーを書き込む
    data_writer.writerow(['posX', 'posY', 'posZ', 'rotX', 'rotY', 'rotZ'])
    filtered_writer.writerow(['posX', 'posY', 'posZ', 'rotX', 'rotY', 'rotZ'])

    cap = cv2.VideoCapture(2)
    # マーカーサイズ
    marker_length = 0.056 # [m]
    # マーカーの辞書選択
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)

    # 閾値フィルタを初期化（閾値は必要に応じて設定）
    threshold_filter = ThresholdFilter(position_threshold=0.3, angle_threshold=30.0)

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
                
                # data.csvに出力
                data_writer.writerow([posX, posY, posZ, rotX, rotY, rotZ])

               # 閾値フィルタを適用
                filtered_data = threshold_filter.apply(np.array([posX, posY, posZ, rotX, rotY, rotZ]))
                
                # filtered_data.csvに出力
                filtered_writer.writerow(filtered_data)

                print(f"x: {filtered_data[0]}, y: {filtered_data[1]}, z: {filtered_data[2]}, roll: {filtered_data[3]}, pitch: {filtered_data[4]}, yaw: {filtered_data[5]}")

                data = f"{filtered_data[0]},{filtered_data[1]},{filtered_data[2]},{filtered_data[3]},{filtered_data[4]},{filtered_data[5]}"

                send_data(data)

                # 可視化
                draw_pole_length = marker_length / 2  # 現実での長さ[m]
                cv2.drawFrameAxes(img, camera_matrix, distortion_coeff, rvec, np.array([filtered_data[0], -filtered_data[1], filtered_data[2]]), draw_pole_length)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
