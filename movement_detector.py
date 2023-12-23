import cv2
import time
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class Settings:
    blur_strength: int
    threshold: int
    dilation_iterations: int


def get_movement_spots(diff, settings: Settings) -> List[Tuple[int, int]]:
    """
    Get the spots where movement is detected.

    The following steps are performed:
    - Absolute difference between current and previous frame
    - Grayscale conversion
    - Gaussian blur
    - Thresholding
    - Dilation
    - Contour detection
    - Contour center calculation

    :param diff: Difference between two consecutive frames.
                 Can be obtained with the following code
                 (frame and prev_frame are grayscale images):

                    diff = cv2.subtract(frame, prev_frame)
                    # Only keep the positive differences
                    diff = np.clip(diff, 0, 255)

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
        diff = cv2.subtract(frame, self.__prev_frame[0])
        # Only keep the positive differences
        diff = np.clip(diff, 0, 255)
        cv2.imshow("diff", diff)
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
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Crop a third of the image from the top and bottom
        height, _ = frame.shape
        frame = frame[int(height / 3) : int((height * 2) / 3), :]
        return frame
