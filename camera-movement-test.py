#!/usr/bin/env python3

# GLOBAL OPTIONS

# Use picamera2 instead of opencv for taking pictures
PICAMERA = False
# Camera device ID, list with ls /dev/video* to find the correct one
CAMERA_ID = 0
# Threshold for the difference between two consecutive values of a pixel to be considered a change
THRESHOLD = 50
# Minimum time between two consecutive pictures. Will be longer if processing takes longer
INTERVAL = 100

# END OF GLOBAL OPTIONS

from typing import List
import cv2 as cv
import numpy as n
import time


# Here goes all that can change between the two camera librarier
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
    ret, grayplus = cv.threshold(img_diff, 127+THRESHOLD, 255, cv.THRESH_BINARY)

    if not ret:
        raise RuntimeError("Threshold failed")

    ret, grayminus = cv.threshold(img_diff, 127-THRESHOLD, 255, cv.THRESH_BINARY_INV)

    if not ret:
        raise RuntimeError("Threshold failed")

    gray = grayplus + grayminus

    # All points that are on
    points = n.argwhere(gray > 0)
    contour_centers = [(int(x), int(y)) for y, x in points]

    # Create an empty Delaunay triangulation
    delaunay = cv.Subdiv2D()

    delaunay.initDelaunay((0, 0, img_diff.shape[1], img_diff.shape[0]))

    # Insert the points into the triangulation
    delaunay.insert(contour_centers)

    # Get the triangles
    triangles = delaunay.getTriangleList()

    # Filter out the triangles that are too long
    triangles = [triangle for triangle in triangles if get_triangle_length(triangle) < 35]
    if len(triangles) == 0:
        return []

    # Draw the triangles on a black image
    img_triangles = cv.cvtColor(n.zeros_like(img_diff), cv.COLOR_GRAY2BGR)
    for triangle in triangles:
        cv.fillConvexPoly(img_triangles, n.array(triangle, dtype=n.int32).reshape(-1, 2), (255, 255, 255))
    
    cv.imshow("triangles", img_triangles)

    # We now want to find the center of each group of triangles
    # We do this by finding the contours of the triangles

    # Convert to grayscale
    img_triangles_gray = cv.cvtColor(img_triangles, cv.COLOR_BGR2GRAY)

    # Threshold
    ret, img_triangles_thresh = cv.threshold(img_triangles_gray, 127, 255, cv.THRESH_BINARY)

    # Find contours
    contours, hierarchy = cv.findContours(img_triangles_thresh, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

    # Draw the contours
    img_contours = cv.cvtColor(n.zeros_like(img_diff), cv.COLOR_GRAY2BGR)
    cv.drawContours(img_contours, contours, -1, (255, 255, 255), 2)
    cv.imshow("contours", img_contours)

    # Get the centers of the contours
    centers = []
    for contour in contours:
        # Get the moments
        moments = cv.moments(contour)

        # Get the center
        center = (moments["m10"] / moments["m00"], moments["m01"] / moments["m00"])

        # Append to the list
        centers.append(center)

    # Combine centers that are close together
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            if n.sqrt((centers[i][0] - centers[j][0])**2 + (centers[i][1] - centers[j][1])**2) < 20:
                if centers[i] is None or centers[j] is None:
                    continue
                centers[i] = ((centers[i][0] + centers[j][0]) / 2, (centers[i][1] + centers[j][1]) / 2)
                centers[j] = None

    return [center for center in centers if center is not None]

def rect_contains(rect, point):
    if point[0] < rect[0]:
        return False
    elif point[1] < rect[1]:
        return False
    elif point[0] > rect[2]:
        return False
    elif point[1] > rect[3]:
        return False
    return True

def get_triangle_length(triangle):
    pt1 = (triangle[0], triangle[1])
    pt2 = (triangle[2], triangle[3])
    pt3 = (triangle[4], triangle[5])

    pt1 = (int(pt1[0]), int(pt1[1]))
    pt2 = (int(pt2[0]), int(pt2[1]))
    pt3 = (int(pt3[0]), int(pt3[1]))

    return max(
        n.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2),
        n.sqrt((pt2[0] - pt3[0])**2 + (pt2[1] - pt3[1])**2),
        n.sqrt((pt3[0] - pt1[0])**2 + (pt3[1] - pt1[1])**2)
    )

if __name__ == "__main__":
    main()
