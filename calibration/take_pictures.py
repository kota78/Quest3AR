import cv2
import os

# カメラの解像度を設定
CAM_WIDTH=3264
CAM_HEIGHT=2448

# 保存ディレクトリ
SAVE_DIR = "captured_images"
os.makedirs(SAVE_DIR, exist_ok=True)  # ディレクトリがなければ作成

# カメラの初期化
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

# 実際に設定された解像度を確認
actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Camera resolution: {actual_width}x{actual_height}")

print("Press 'Enter' to capture an image or 'q' to quit.")

image_counter = 0

try:
    while True:
        # フレームを取得
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break

        # カメラ画像を表示
        cv2.imshow("Camera", frame)

        # キー入力待ち
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Exiting...")
            break
        elif key == 13:  # Enterキーが押された場合
            image_counter += 1
            filename = os.path.join(SAVE_DIR, f"image_{image_counter:03d}.png")
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")

finally:
    # リソースを解放
    cap.release()
    cv2.destroyAllWindows()