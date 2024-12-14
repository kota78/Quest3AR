#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import aruco
import socket
import threading
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
    cap = cv2.VideoCapture(0)
    # 解像度を設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    # 実際に設定された解像度を取得
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 設定結果を確認
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

                # # オイラー角を送信する場合
                # rvec[0]=-rvec[0]？
                # rvec[2]=-rvec[2]？
                # rvec_matrix = cv2.Rodrigues(rvec) # 回転ベクトルからrodoriguesへ変換
                # rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し
                # transpose_tvec = tvec[np.newaxis, :].T # 並進ベクトルの転置
                # proj_matrix = np.hstack((rvec_matrix, transpose_tvec)) # 合成
                # euler_angle = cv2.decomposeProjectionMatrix(proj_matrix)[6] # オイラー角への変換
                # rotX, rotY, rotZ = euler_angle[0, 0], euler_angle[1, 0], euler_angle[2, 0]
                # data = f"{ids[i][0]},{posX},{posY},{posZ},{rotX},{rotY},{rotZ}"

                # クオータニオンを送信する場合
                # 回転ベクトル -> Rotationクラスのrotationオブジェクト
                rvec[0]=-rvec[0]
                rvec[2]=-rvec[2]
                rotation = R.from_rotvec(rvec)
                # Rotationクラスのrotationオブジェクト -> クォータニオン
                quaternion = rotation.as_quat()
                data = f"{ids[i][0]},{posX},{posY},{posZ},{quaternion[0]},{quaternion[1]},{quaternion[2]},{quaternion[3]}"

                # 正規化する場合
                # rotX, rotY, rotZ = normalize_angle(euler_angle[0, 0]+180), normalize_angle(euler_angle[1, 0]), normalize_angle(euler_angle[2, 0])

                # フォーマット済みデータ
                # data = f"{format_value(posX)},{format_value(posY)},{format_value(posZ)},{format_value(rotX)},{format_value(rotY)},{format_value(rotZ)}"
                # data = f"{format_value(posX)},{format_value(posY)},{format_value(posZ)},{format_value(rotX)},{format_value(rotY)},{format_value(rotZ)}"

                data_list.append(data)
                # print(data)

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

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
