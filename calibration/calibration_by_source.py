#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import glob

square_size = 2.0      # 正方形の1辺のサイズ[cm]
pattern_size = (6, 9)  # チェスボードの交差ポイント数

# チェスボードの3D座標を設定 (Z=0)
pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
pattern_points *= square_size

objpoints = []  # 3D座標点
imgpoints = []  # 2D画像点

# ソース画像ディレクトリ内の画像を読み込む
images = glob.glob('source/*.jpg')  # 画像が入っているフォルダを指定

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # チェスボードのコーナーを検出
    ret, corners = cv2.findChessboardCorners(gray, pattern_size)
    if ret:
        print(f"Detected corners in {fname}")
        term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
        cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), term)
        imgpoints.append(corners.reshape(-1, 2))
        objpoints.append(pattern_points)

        # 検出結果を描画して確認（オプション）
        cv2.drawChessboardCorners(img, pattern_size, corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# カメラキャリブレーションを計算
print("Calculating camera parameters...")
print('objpoints:', objpoints)
print('imgpoints:', imgpoints)
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# 計算結果を保存
np.save("mtx.npy", mtx)  # カメラ行列
np.save("dist.npy", dist.ravel())  # 歪みパラメータ

# 計算結果を表示
print("RMS = ", ret)
print("Camera matrix (mtx) = \n", mtx)
print("Distortion coefficients (dist) = ", dist.ravel())
