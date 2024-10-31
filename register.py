import cv2
import numpy as np

def register_custom_marker(image_path):
    marker = cv2.imread(image_path, 0)  # グレースケールで画像を読み込む
    _, binary_marker = cv2.threshold(marker, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 2値化
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(binary_marker, None)  # 2値画像で特徴点を検出
    return binary_marker, keypoints, descriptors

def visualize_keypoints(image, keypoints):
    img_with_keypoints = cv2.drawKeypoints(image, keypoints, None, color=(0, 255, 0), flags=0)
    cv2.imshow("Keypoints", img_with_keypoints)
    while True:
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

# マーカー登録
marker_path = "kabochan_face1.jpg"
marker, marker_keypoints, marker_descriptors = register_custom_marker(marker_path)

# 特徴点の可視化
print(f"Number of keypoints detected: {len(marker_keypoints)}")
visualize_keypoints(marker, marker_keypoints)
