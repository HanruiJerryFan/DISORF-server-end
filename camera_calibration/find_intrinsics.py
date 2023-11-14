import numpy as np
import cv2
import glob
import json

# Checkerboard dimensions
CHECKERBOARD = (7, 5)

# Termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Object points
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

# Arrays to store object and image points
objpoints = [] 
imgpoints = [] 

# Images path
images_path = glob.glob('./images/*.jpg')

# Initialize variables for image dimensions
H, W = None, None

for img_path in images_path:
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Store image dimensions
    if H is None or W is None:
        H, W = gray.shape[:2]

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw corners (optional)
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# Camera calibration
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Extracting parameters
fx = mtx[0, 0]
fy = mtx[1, 1]
cx = mtx[0, 2]
cy = mtx[1, 2]
k1, k2, p1, p2, k3 = dist[0]

# Additional placeholders (replace with actual values)
image_topic = "/image_raw"  # Replace with actual image topic
pose_topic = "/pose"  # Replace with actual pose topic

# Organize data into a dictionary
camera_intrinsics = {
    "fx": fx,
    "fy": fy,
    "cx": cx,
    "cy": cy,
    "k1": k1,
    "k2": k2,
    "k3": k3,
    "p1": p1,
    "p2": p2,
    "H": H,
    "W": W,
    "image_topic": image_topic,
    "pose_topic": pose_topic
}

# Write to a JSON file
with open('camera_intrinsics.json', 'w') as outfile:
    json.dump(camera_intrinsics, outfile, indent=4)

print("Camera intrinsics saved to camera_intrinsics.json")
