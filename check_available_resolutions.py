import cv2

def list_available_resolutions(camera_index=0):
    # カメラを初期化
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("カメラが開けませんでした。")
        return

    # 解像度リスト（一般的な解像度を試す）
    common_resolutions = [
        (3840, 2160),  # 4K
        (2560, 1440),  # 2K
        (1920, 1080),  # Full HD
        (1024,768),
        (3264, 2448),
        (1280, 720),   # HD
        (640, 480),    # VGA
        (320, 240),    # QVGA
        (160, 120)     # QQVGA
    ]

    available_resolutions = []

    for width, height in common_resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if int(actual_width) == width and int(actual_height) == height:
            available_resolutions.append((int(actual_width), int(actual_height)))

    cap.release()

    print("使用可能な解像度:")
    for resolution in available_resolutions:
        print(f"{resolution[0]}x{resolution[1]}")

list_available_resolutions()
