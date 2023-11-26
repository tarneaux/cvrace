#!/usr/bin/env python3

# GLOBAL OPTIONS

# Use picamera2 instead of opencv for taking pictures
PICAMERA = False
# Camera device ID, list with ls /dev/video* to find the correct one
CAMERA_ID = 0
# Threshold for the difference between two consecutive values of a pixel to be considered a change
THRESHOLD = 50
# Minimum time between two consecutive pictures. Will be longer if processing takes longer
INTERVAL = 50

# END OF GLOBAL OPTIONS

from typing import List
import cv2 as cv
import numpy as n
import time


# Here goes all that can change between the two camera libraries
if PICAMERA:
    from picamera2 import Picamera2

    picam = Picamera2()
    # picam2.configure(picam2.create_still_configuration({"size":(4056, 3040)})) # Slows down
    picam.start(show_preview=False)
    getImg = lambda: (True, picam.capture_array())
else:
    cam = cv.VideoCapture(CAMERA_ID)
    getImg = lambda: cam.read()


def main():
    img_previous = None
    while True:
        start_time = int(time.time() * 1000)

        # Take a picture
        ret, img = getImg()

        if not ret:
            print("Camera read failed")
            continue

        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # imgGray = cv.resize(imgGray, (507, 380))

        if img_previous is not None:
            img_diff = process_image(img_gray, img_previous)
            cv.imshow("diff", img_diff)
        else:
            cv.imshow("diff", img_gray)

        img_previous = img_gray

        if start_time is not None:
            currenttime = int(time.time() * 1000)
            print(f"Time to take picture: {currenttime - start_time}")
            tosleep = start_time + INTERVAL - currenttime
            tosleep = max(tosleep, 1)
            print(f"Time to wait to complete {INTERVAL}ms interval: {tosleep}")
            key = cv.waitKey(int(tosleep)) & 0xFF
            if key == ord("q"):
                break


def process_image(img_gray, previous_image):
    img_diff = img_gray - previous_image + 127

    # Get object positions
    positions = get_object_positions(img_diff)

    for x, y in positions:
        # Draw a circle at the mean X and Y
        cv.circle(img_diff, (int(x), int(y)), 10, (0, 0, 0), 2)

    return img_diff

def get_object_positions(img_diff) -> List[tuple[float, float]]:
    ret, grayplus = cv.threshold(img_diff, 127+THRESHOLD, 255, cv.THRESH_TOZERO)

    if not ret:
        print("Threshold failed")
        raise RuntimeError("Threshold failed")

    ret, grayminus = cv.threshold(img_diff, 127-THRESHOLD, 255, cv.THRESH_TOZERO_INV)

    if not ret:
        print("Threshold failed")
        raise RuntimeError("Threshold failed")

    gray = grayplus + grayminus

    # Find contours
    contours, hierarchy = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Get the center of each contour
    contour_centers = []
    for contour in contours:
        M = cv.moments(contour)
        if M["m00"] != 0:
            x = M["m10"] / M["m00"]
            y = M["m01"] / M["m00"]
            contour_centers.append((x, y))

    lines = []
    for x, y in contour_centers:
        closest = get_closest(contour_centers, x, y, 4)
        for x2, y2 in closest[1:]: # Skip the first one, which is the same as the current one
            lines.append((x, y, x2, y2))

    # Remove duplicates
    lines = list(set(lines))

    # Create a black image
    line_img = cv.cvtColor(n.zeros_like(img_diff), cv.COLOR_GRAY2BGR)

    for x1, y1, x2, y2 in lines:
        cv.line(line_img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 2)

    cv.imshow("lines", line_img)

    return []

def get_closest(coords_list, x, y, count):
    distances = [
        (i, n.linalg.norm(n.array((x, y)) - n.array((x2, y2))))
        for i, (x2, y2) in enumerate(coords_list)
    ]

    distances.sort(key=lambda x: x[1])

    return [coords_list[i] for i, _ in distances[:count]]

if __name__ == "__main__":
    main()
