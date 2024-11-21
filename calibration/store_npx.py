import numpy as np

# カメラ行列と歪み係数
camera_matrix = np.array([[464.76830292, 0, 512.35210634],
                          [0, 469.61837529, 385.2203724],
                          [0, 0, 1]])
distortion_coeff = np.array([-0.3136963, 0.10256045, -0.01269226, 0.00985827, -0.01445209])

# 保存
np.save("old_mtx.npy", camera_matrix)
np.save("old_dist.npy", distortion_coeff)

print("Saved camera matrix to 'old_mtx.npy'")
print("Saved distortion coefficients to 'old_dist.npy'")
