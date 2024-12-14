import os
import sys
import cv2
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import CAMERA_MATRIX, DISTORTION_COEFF

def main():
    # 画像ソースの切り替え
    use_camera = False  # Trueにするとカメラ撮影、Falseにすると画像ファイルを使用

    if use_camera:
        # カメラから画像を取得
        capture = cv2.VideoCapture(0)
        ret, frame = capture.read()
        if not ret:
            print("Failed to capture image from camera.")
            capture.release()
            exit()
        img = frame
        capture.release()
    else:
        # ファイルから画像を読み込む
        img = cv2.imread("calibration/captured_images/image_001.png")
        if img is None:
            print("Failed to load image from file.")
            exit()

    # 元画像
    h, w = img.shape[:2]

    # 歪み補正: OLD_CAMERA_MATRIX と OLD_DISTORTION_COEFF を使用
    old_new_camera_mtx, old_roi = cv2.getOptimalNewCameraMatrix(CAMERA_MATRIX, DISTORTION_COEFF, (w, h), 1, (w, h))
    old_undistorted_img = cv2.undistort(img, CAMERA_MATRIX, DISTORTION_COEFF, None, old_new_camera_mtx)

    # 歪み補正: CAMERA_MATRIX と DISTORTION_COEFF を使用
    new_new_camera_mtx, new_roi = cv2.getOptimalNewCameraMatrix(CAMERA_MATRIX, DISTORTION_COEFF, (w, h), 1, (w, h))
    new_undistorted_img = cv2.undistort(img, CAMERA_MATRIX, DISTORTION_COEFF, None, new_new_camera_mtx)
    # 画像を横に並べる
    combined_img = np.hstack((img, old_undistorted_img, new_undistorted_img))

    # 結果を表示
    cv2.imshow("Comparison: Original | Old Calibration | New Calibration", combined_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
