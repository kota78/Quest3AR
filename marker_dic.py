import cv2
import numpy as np
from cv2 import aruco
import pickle

def create_custom_marker_dictionary(image_path, marker_id, marker_size):
    # 画像を読み込み
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # 画像のサイズを確認
    if img.shape[0] != marker_size or img.shape[1] != marker_size:
        # 画像を指定のサイズにリサイズ
        img = cv2.resize(img, (marker_size, marker_size))
    
    # 二値化（マーカーは白黒である必要があります）
    _, binary_marker = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    
    # カスタム辞書を作成
    custom_dict = aruco.custom_dictionary(1, marker_size, 1)
    custom_dict.bytesList[marker_id] = aruco.Dictionary_getByteListFromBits(binary_marker)

    return custom_dict

def save_custom_dictionary(dictionary, filename):
    with open(filename, 'wb') as f:
        pickle.dump(dictionary, f)
    print(f"Custom dictionary saved to {filename}")

def load_custom_dictionary(filename):
    with open(filename, 'rb') as f:
        dictionary = pickle.load(f)
    print(f"Custom dictionary loaded from {filename}")
    return dictionary

# 使用例
image_path = 'kabochan_face1.jpg'  # 好きな画像のパス
marker_id = 0  # マーカーID
marker_size = 3024  # マーカーのサイズ

def main():
    custom_dict = create_custom_marker_dictionary(image_path, marker_id, marker_size)
    save_custom_dictionary(custom_dict, 'custom_marker_dict.pkl')

if __name__ == '__main__':
    main()


# カスタム辞書を生成
custom_dict = create_custom_marker_dictionary(image_path, marker_id, marker_size)

# 辞書を保存
save_custom_dictionary(custom_dict, 'custom_marker_dict.pkl')

# 辞書を読み込み
loaded_dict = load_custom_dictionary('custom_marker_dict.pkl')
