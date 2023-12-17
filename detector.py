#!/usr/bin/env python3
import cv2
import time
import csv
from dataclasses import dataclass
import numpy as np
from typing import List, Tuple

CAMERA_ID = 0


@dataclass
class Settings:
    blur_strength: int
    threshold: int
    dilation_iterations: int


def get_movement_spots(diff, settings: Settings) -> List[Tuple[int, int]]:
    """
    Get the spots where movement is detected.
    This function uses a combination of image processing techniques to detect
    movement. These include:
    - Absolute difference between current and previous frame
    - Grayscale conversion
    - Gaussian blur
    - Thresholding
    - Dilation
    - Contour detection
    - Contour center calculation
    :param diff: Difference between two consecutive frames.
                 Can be obtained with cv2.absdiff() on two frames.
    :return: List of spots where movement is detected
    """
    blur = cv2.GaussianBlur(diff, (settings.blur_strength, settings.blur_strength), 0)
    _, thresh = cv2.threshold(blur, settings.threshold, 255, cv2.THRESH_BINARY)
    # Dilation is used to fill in the gaps between contours
    dilated = cv2.dilate(thresh, None, iterations=settings.dilation_iterations)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # Get the centers of the contours
    centers = get_contour_centers(contours)
    return centers


def get_contour_centers(contours) -> List[Tuple[int, int]]:
    contours = [cv2.moments(c) for c in contours]

    def get_contour_center(m):
        try:
            return (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))
        except ZeroDivisionError:
            return None

    centers = [get_contour_center(m) for m in contours]
    return [c for c in centers if c is not None]


def show_preview(frame, object_positions: list):
    """
    Show a preview of the camera's view, and the detected movement.
    :param frame: Frame to show
    :param object_positions: List of positions where movement is detected
    """
    preview = frame.copy()
    for center in object_positions:
        cv2.circle(preview, center, 10, (0, 255, 0), -1)
    cv2.imshow("preview", preview)


class MovementDetector:
    def __init__(self, settings: Settings, camera_id: int):
        """
        :param capture_function: Function that returns a frame
        :param settings: Settings for the movement detector
        """
        self.__settings = settings
        self.__cap = cv2.VideoCapture(camera_id)
        self.reset()

    def reset(self):
        """
        Reset the movement detector by taking a new previous frame.
        """
        self.__prev_frame = (self.__get_image(), time.time())

    def detect_movement(self) -> Tuple[float, List[Tuple[int, int]]]:
        """
        Detect movement in the next frame.
        :return: Time of the difference, and a list of positions where movement
            was detected
        """
        capture_time = time.time()
        frame = self.__get_image()
        diff = cv2.absdiff(frame, self.__prev_frame[0])
        object_positions = get_movement_spots(diff, self.__settings)
        mean_time = (capture_time + self.__prev_frame[1]) / 2
        self.__prev_frame = (frame, capture_time)
        return (mean_time, object_positions)

    def get_previous_frame(self):
        """
        Get the previous frame.
        :return: Previous frame
        """
        if self.__prev_frame is not None:
            return self.__prev_frame[0]
        else:
            raise Exception("No previous frame")

    def __get_image(self):
        ret, frame = self.__cap.read()
        if not ret:
            raise Exception("Could not read frame from camera")
        # Crop a third of the image from the top and bottom
        height, _, _ = frame.shape
        frame = frame[height // 3 : height // 3 * 2, :]
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def main():
    detector = MovementDetector(Settings(15, 20, 15), CAMERA_ID)
    position_history = []
    while True:
        try:
            t = time.time()
            capture_time, object_positions = detector.detect_movement()
            position_history.append((capture_time, object_positions))
            show_preview(detector.get_previous_frame(), object_positions)
            key = cv2.waitKey(1)
            # Limit to 4 FPS
            time_taken = time.time() - t

            to_sleep = max(0, 0.2 - time_taken)

            print(f"Time taken: {time_taken}")

            time.sleep(max(0, to_sleep))

            if to_sleep == 0:
                print(f"Lagging behind!")

            if key == ord("q"):
                break
        except KeyboardInterrupt:
            break

    # Write the positions to a CSV file
    with open("positions.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["time", "x", "y"])
        for t, positions in position_history:
            for x, y in positions:
                writer.writerow([t, x, y])

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
