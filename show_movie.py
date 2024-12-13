import cv2
import time

def display_camera_feed(camera_index=0, width=3264, height=2448, fps=15):
    # カメラを初期化
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("カメラが開けませんでした。")
        return

    # 解像度とフレームレートを設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)

    # 実際に設定された値を取得
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"設定解像度: {width}x{height} @ {fps}fps")
    print(f"実際の解像度: {actual_width}x{actual_height}")
    print(f"実際のフレームレート: {actual_fps}fps")

    # フレームを表示し続ける
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        print(ret)

        # フレームをウィンドウに表示
        cv2.imshow("Camera Feed", frame)

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # フレームレートを維持するためのスリープ
        elapsed_time = time.time() - start_time
        sleep_time = max(1.0 / fps - elapsed_time, 0)
        time.sleep(sleep_time)

    # リソース解放
    cap.release()
    cv2.destroyAllWindows()

# 実行
display_camera_feed()
