import cv2

def display_camera_feed(camera_index=0, width=3264, height=2448):
    # カメラを初期化
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("カメラが開けませんでした。")
        return

    # 解像度を設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # 実際に設定された解像度を取得
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"設定解像度: {width}x{height}")
    print(f"実際の解像度: {actual_width}x{actual_height}")

    # フレームを表示
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("カメラからフレームを取得できませんでした。")
            break

        # ウィンドウにフレームを表示
        cv2.imshow("Camera Feed", frame)

        # 'q'キーが押されたら終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # リソース解放
    cap.release()
    cv2.destroyAllWindows()

# 実行
display_camera_feed()
