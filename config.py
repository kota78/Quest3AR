import numpy as np


UDP_IP = "192.168.11.99"
KACHAKA_IP='192.168.11.27'
TCP_HOST_IP = '0.0.0.0'
UDP_PORT = 50000
TCP_PORT = 50001
CAMERA_MATRIX = np.array(
[[1.01768272e+03, 0.00000000e+00, 7.55164703e+02],
 [0.00000000e+00, 1.00070184e+03, 4.19396906e+02],
 [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]
)

DISTORTION_COEFF = np.array(
[-0.85235072, 0.61171403, -0.00922097, -0.00873951, -0.16635098]
)


OLD_CAMERA_MATRIX = np.array([[464.76830292,0,512.35210634],
                              [0,469.61837529,385.2203724],
                              [0, 0, 1]])

OLD_DISTORTION_COEFF = np.array([-0.3136963, 0.10256045, -0.01269226, 0.00985827, -0.01445209])