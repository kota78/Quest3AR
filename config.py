import numpy as np


# UDP_IP = "192.168.11.99"
# UDP_IP = "0.0.0.0"
# UDP_IP = "127.0.0.1"
UDP_IP = "192.168.11.99"
KACHAKA_IP = "192.168.11.27"
TCP_HOST_IP = "0.0.0.0"
UDP_PORT = 50000
TCP_PORT = 50001
MARKER_LENGTH = 0.084  # [m]
CAMERA_ID = 3


def get_camera_config(camera_id=CAMERA_ID):
    if camera_id in camera_configs:
        config = camera_configs[camera_id]
        print("camera_id:" + str(camera_id))
        return (
            config["CAM_WIDTH"],
            config["CAM_HEIGHT"],
            config["CAMERA_MATRIX"],
            config["DISTORTION_COEFF"],
        )
    else:
        raise ValueError(
            f"Invalid camera ID: {camera_id}. Available IDs: {list(camera_configs.keys())}"
        )


camera_configs = {
    # 180 1024x768
    1: {
        "CAM_HEIGHT": 768,
        "CAM_WIDTH": 1024,
        "CAMERA_MATRIX": np.array(
            [[464.76830292, 0, 512.35210634], [0, 469.61837529, 385.2203724], [0, 0, 1]]
        ),
        "DISTORTION_COEFF": np.array(
            [-0.3136963, 0.10256045, -0.01269226, 0.00985827, -0.01445209]
        ),
    },
    # 180 3264x2448
    2: {
        "CAM_HEIGHT": 2448,
        "CAM_WIDTH": 3264,
        "CAMERA_MATRIX": np.array(
            [
                [1.43689861e03, 0, 1.64483653e03],
                [0, 1.49759081e03, 1.20146178e03],
                [0, 0, 1],
            ]
        ),
        "DISTORTION_COEFF": np.array(
            [-0.25387412, 0.03443582, -0.00970638, -0.00684306, 0.0113366]
        ),
    },
    # 75 1024 x 768
    3: {
        "CAM_HEIGHT": 768,
        "CAM_WIDTH": 1024,
        # RMS =  1.1436840974632059
        "CAMERA_MATRIX": np.array(
            [
                [1.88193221e03, 0, 5.67457603e02],
                [0, 1.86811601e03, 2.24800455e02],
                [0, 0, 1],
            ]
        ),
        "DISTORTION_COEFF": np.array(
            [0.46087888, -3.429609, -0.02459316, 0.00768441, -5.43554961]
        ),
    },
    # 75 3264x2448
    # RMS =  1.7244738736276344
    4: {
        "CAM_HEIGHT": 2448,
        "CAM_WIDTH": 3264,
        "CAMERA_MATRIX": np.array(
            [
                [2.68314817e03, 0, 1.76952595e03],
                [0, 2.69018846e03, 1.56106567e03],
                [0, 0, 1],
            ]
        ),
        "DISTORTION_COEFF": np.array(
            [0.0608363, -0.00764658, 0.02305972, 0.02113898, 0.00273034]
        ),
    },
    # 180 3264x2448 ChArucoでのキャリブレーション
    5: {
        "CAM_HEIGHT": 2448,
        "CAM_WIDTH": 3264,
        "CAMERA_MATRIX": np.array(
            [
                [1.11272836e03, 0, 1.61212810e03],
                [0, 1.11272836e03, 1.24198815e03],
                [0, 0, 1],
            ]
        ),
        "DISTORTION_COEFF": np.array(
            [
                [5.55030376e-01],
                [3.89677455e-02],
                [-3.42657612e-05],
                [3.29036952e-05],
                [7.71105709e-05],
                [8.97739703e-01],
                [1.49387232e-01],
                [2.53392451e-03],
                [0.00000000e00],
                [0.00000000e00],
                [0.00000000e00],
                [0.00000000e00],
                [0.00000000e00],
                [0.00000000e00],
            ]
        ),
    },
    # 魚眼じゃないカメラ（先生からかりたやつ）
    6: {
        "CAM_HEIGHT": 768,
        "CAM_WIDTH": 1024,
        "CAMERA_MATRIX": np.array(
            [
                [1.38575451e03, 0, 6.36114324e02],
                [0.00000000e00, 1.38673291e03, 3.83136104e02],
                [0, 0, 1],
            ]
        ),
        "DISTORTION_COEFF": np.array(
            [
                1.83859000e-01,
                -7.81523173e-01,
                -5.03588300e-03,
                5.33068188e-04,
                1.16666801e00,
            ]
        ),
    },
}
