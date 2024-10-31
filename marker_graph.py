#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import aruco
import socket
import time
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# UDP送信設定
UDP_IP = "192.168.11.4"
UDP_PORT = 50000

sock = socket.socket(socket.SOCK_DGRAM)

def send_data(data):
    sock.sendto(data.encode('utf-8'), (UDP_IP, UDP_PORT))

def main():
    cap = cv2.VideoCapture(0)
    marker_length = 0.056  # マーカーサイズ[m]
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)

    camera_matrix = np.array([[464.76830292, 0, 512.35210634],
                              [0, 469.61837529, 385.2203724],
                              [0, 0, 1]])
    distortion_coeff = np.array([-0.3136963, 0.10256045, -0.01269226, 0.00985827, -0.01445209])

    collected_data = []
    start_time = time.time()

    while time.time() - start_time < 10:  # 10秒間データを収集
        ret, img = cap.read()
        img = cv2.flip(img, -1)
        corners, ids, _ = aruco.detectMarkers(img, dictionary)
        aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 255))

        if len(corners) > 0:
            for corner in corners:
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, marker_length, camera_matrix, distortion_coeff)
                tvec = np.squeeze(tvec)

                posX, posY, posZ = tvec[0], -tvec[1], tvec[2]  # Y座標を反転

                collected_data.append([posX, posY, posZ])

                # データ送信
                data = f"{posX},{posY},{posZ}"
                # send_data(data)

                # 可視化
                draw_pole_length = marker_length / 2
                cv2.drawFrameAxes(img, camera_matrix, distortion_coeff, rvec, tvec, draw_pole_length)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # データをNumPy配列に変換
    collected_data = np.array(collected_data)

    # 周波数解析
    sample_rate = len(collected_data) / 10  # 10秒間のサンプル数を使用してサンプルレートを計算
    N = len(collected_data)

    # 各軸のフーリエ変換
    posX_fft = fft(collected_data[:, 0])
    posY_fft = fft(collected_data[:, 1])
    posZ_fft = fft(collected_data[:, 2])

    freqs = fftfreq(N, 1 / sample_rate)

    # 絶対値を取りゲインを計算
    gain_posX = np.abs(posX_fft)
    gain_posY = np.abs(posY_fft)
    gain_posZ = np.abs(posZ_fft)

    # 結果をprintで出力
    print("\n=== X Axis Frequency and Gain ===")
    for f, g in zip(freqs[:N // 2], gain_posX[:N // 2]):
        print(f"Frequency: {f:.2f} Hz, Gain: {g:.2f}")

    print("\n=== Y Axis Frequency and Gain ===")
    for f, g in zip(freqs[:N // 2], gain_posY[:N // 2]):
        print(f"Frequency: {f:.2f} Hz, Gain: {g:.2f}")

    print("\n=== Z Axis Frequency and Gain ===")
    for f, g in zip(freqs[:N // 2], gain_posZ[:N // 2]):
        print(f"Frequency: {f:.2f} Hz, Gain: {g:.2f}")

    # グラフ描画
    plt.figure(figsize=(12, 6))
    
    plt.subplot(3, 1, 1)
    plt.plot(freqs[:N // 2], gain_posX[:N // 2])
    plt.title('X Axis Gain vs Frequency')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Gain')

    plt.subplot(3, 1, 2)
    plt.plot(freqs[:N // 2], gain_posY[:N // 2])
    plt.title('Y Axis Gain vs Frequency')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Gain')

    plt.subplot(3, 1, 3)
    plt.plot(freqs[:N // 2], gain_posZ[:N // 2])
    plt.title('Z Axis Gain vs Frequency')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Gain')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
