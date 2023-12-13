#!/usr/bin/env python3
import cv2
import time
import csv
from dataclasses import dataclass

CAMERA_ID = 0

@dataclass
class Settings:
    blur_strength: int
    threshold: int
    dilation_iterations: int

def get_movement_spots(diff, settings: Settings) -> list:
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
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (settings.blur_strength, settings.blur_strength), 0)
    _, thresh = cv2.threshold(blur, settings.threshold, 255, cv2.THRESH_BINARY)
    # Dilation is used to fill in the gaps between contours
    dilated = cv2.dilate(thresh, None, iterations=settings.dilation_iterations)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # Get the centers of the contours
    centers = get_contour_centers(contours)
    return centers

def get_contour_centers(contours) -> list:
    contours = [cv2.moments(c) for c in contours]
    try:
        return [
            (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
            for m in contours
        ]
    except ZeroDivisionError:
        print('ZeroDivisionError')
        return []

class MovementDetector:
    def __init__(self, settings: Settings):
        """
        :param capture_function: Function that returns a frame
        """
        self.settings = settings
        self.prev_frame = None # Will be a tuple of (frame, time)
        self.cap = cv2.VideoCapture(CAMERA_ID)
        self.continue_loop = True # Used for background thread
        self.preview = False # Whether to show a preview of the camera
        # List of positions at times when movement was detected
        self.positions = []

    def detect_movement(self):
        """
        Detect movement in the next frame.
        :return: List of spots where movement is detected
        """
        capture_time = time.time()
        ret, frame = self.cap.read()
        if not ret:
            raise Exception('Could not read frame from camera')
        if self.prev_frame is not None:
            diff = cv2.absdiff(frame, self.prev_frame[0])
            object_positions = get_movement_spots(diff, self.settings)
            mean_time = (capture_time + self.prev_frame[1]) / 2
            self.positions.append((mean_time, object_positions))
            self.prev_frame = (frame, capture_time)
            return object_positions
        else:
            self.prev_frame = (frame, capture_time)
            return []

    def reset(self):
        """
        Reset the movement detector.
        """
        self.prev_frame = None

    def show_preview(self):
        """
        Show a preview of the camera's view, and the detected movement.
        """
        if self.prev_frame is None or self.positions == []:
            return
        preview = self.prev_frame[0].copy()
        # black = np.zeros_like(self.prev_frame[0])
        for center in self.positions[-1][1]:
            cv2.circle(preview, center, 10, (0, 255, 0), -1)
        cv2.imshow('preview', preview)

def main():
    detector = MovementDetector(Settings(15, 20, 15))
    while True:
        try:
            t = time.time()
            detector.detect_movement()
            detector.show_preview()
            key = cv2.waitKey(1)
            # Limit to 4 FPS
            to_sleep = (1 / 4) - (time.time() - t)
            time.sleep(max(0, to_sleep))
            print(f'FPS: {int(1 / (time.time() - t))}')
            if to_sleep > 0:
                print(f'Fast enough')
            if key == ord('q'):
                break
        except KeyboardInterrupt:
            break

    # Write the positions to a CSV file
    with open('positions.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['time', 'x', 'y'])
        for t, positions in detector.positions:
            for x, y in positions:
                writer.writerow([t, x, y])

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

