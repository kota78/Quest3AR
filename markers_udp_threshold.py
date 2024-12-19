import numpy as np
import cv2
from cv2 import aruco
import socket
import time
from scipy.spatial.transform import Rotation as R
import csv
from config import (
    UDP_IP,
    UDP_PORT,
    MARKER_LENGTH,
    get_camera_config,
)

CAMERA_ID = 2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_data(data):
    sock.sendto(data.encode("utf-8"), (UDP_IP, UDP_PORT))


# クオータニオン間の角度
def dist_q(q1, q2):
    value = 2 * np.arccos(np.dot(q1.elements, q2.elements))
    print(value)
    return value


def is_small_angle(q1, q2, threshold):
    return abs(dist_q(q1, q2)) < threshold


def main():
    cap = cv2.VideoCapture(0)
    # 解像度を設定
    CAM_WIDTH, CAM_HEIGHT, CAMERA_MATRIX, DISTORTION_COEFF = get_camera_config(
        CAMERA_ID
    )
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"{actual_width}x{actual_height}")

    # マーカーの辞書選択
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    # 処理時間を保存するリスト
    time_measurements = []
    quaternion_map = {}

    while True:
        t1 = time.time()
        ret, img = cap.read()
        t2 = time.time()
        img = cv2.flip(img, -1)
        data_list = []
        exceedCount = 0

        ### 各マーカごとに閾値超えた回数をカウントする必要がありますね。。。

        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)
        if len(corners) > 0:
            exceedCount = 0
            # マーカーごとに処理
            for i, corner in enumerate(corners):
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(
                    corner, MARKER_LENGTH, CAMERA_MATRIX, DISTORTION_COEFF
                )
                # 不要なaxisを除去
                tvec = np.squeeze(tvec)
                rvec = np.squeeze(rvec)
                posX, posY, posZ = tvec[0], tvec[1], tvec[2]
                rvec[0] = -rvec[0]
                rvec[2] = -rvec[2]
                # 回転ベクトル -> Rotationクラスのrotationオブジェクト
                rotation = R.from_rotvec(rvec)
                # Rotationクラスのrotationオブジェクト -> クォータニオン
                quaternion = rotation.as_quat()
                # クォータニオンの前回との差が角度が一定以上の場合送信しない
                if (
                    not is_small_angle(quaternion_map[str(ids[i][0])], quaternion, 30)
                    and exceedCount < 5
                ):
                    exceedCount += 1
                else:
                    data = f"{ids[i][0]},{posX},{posY},{posZ},{quaternion[0]},{quaternion[1]},{quaternion[2]},{quaternion[3]}"
                    data_list.append(data)
                    quaternion_map[str(ids[i][0])] = quaternion

                # 可視化
                # aruco.drawDetectedMarkers(img, corners, ids, (0, 255, 255))
                # draw_pole_length = MARKER_LENGTH /
                # cv2.drawFrameAxes(
                #     img, CAMERA_MATRIX, DISTORTION_COEFF, rvec, tvec, draw_pole_length
                # )

        t3 = time.time()
        if data_list:
            combined_data = ";".join(data_list)
            send_data(combined_data)
            print(combined_data)

        t4 = time.time()

        # 処理時間をリストに保存
        time_measurements.append([t2 - t1, t3 - t2, t4 - t3, t4 - t1])

        # 可視化
        # cv2.imshow("drawDetectedMarkers", img)

        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    # 処理時間をCSVファイルに書き込む
    with open("processing_times.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            [
                "Frame Capture (t2-t1)",
                "Processing (t3-t2)",
                "Sending (t4-t3)",
                "Total Time (t4-t1)",
            ]
        )
        csv_writer.writerows(time_measurements)


if __name__ == "__main__":
    main()
