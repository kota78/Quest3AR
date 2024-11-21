import numpy as np

# 読み込み
camera_matrix = np.load("mtx.npy")
distortion_coeff = np.load("dist.npy")

print("Loaded camera matrix:")
print(camera_matrix)
print("\nLoaded distortion coefficients:")
print(distortion_coeff)
