#!/usr/bin/env python3
import cv2 as cv
import time
import csv
from movement_detector import MovementDetector, Settings

CAMERA_ID = 0
FPS = 10


def show_preview(frame, object_positions: list):
    """
    Show a preview of the camera's view, and the detected movement.
    :param frame: Frame to show
    :param object_positions: List of positions where movement is detected
    """
    preview = frame.copy()
    for center in object_positions:
        cv.circle(preview, center, 10, (0, 255, 0), -1)
    cv.imshow("preview", preview)

class FpsRegulator:
    def __init__(self, fps: int):
        self.__fps = fps
        self.__frame_time = time.monotonic_ns()

    def wait_until_next_frame(self):
        """
        Should be called at the start of the processing of each frame.
        If we are lagging behind, frames will be dropped.
        """
        while True:
            # We round the division here, but it doesn't really matter since we
            # just want to have constant time between frames (plus we're doing
            # it over 1e9, so the error is very small)
            self.__frame_time = self.__frame_time + (1e9 // self.__fps)

            current_time = time.monotonic_ns()

            # Calculate how long we should sleep
            to_sleep = self.__frame_time - current_time
            if to_sleep > 0:
                # Unfortunately, there is no nanosleep function in Python, so
                # we have to use the sleep function which will suffer from
                # floating point errors; but since we already captured time
                # with nanosecond precision, this is not so much of a problem:
                # the drift caused by the error will be cancelled out the next
                # time we call this function.
                time.sleep(to_sleep / 1e9)
                break
            else:
                print("Warning: lagging behind by", -to_sleep, "ns")
                print("Dropping frame")
                # Wait until the next frame by staying in this loop

    def current_frame_time_ns(self):
        return self.__frame_time

def main():
    settings = Settings(15, 10, 15)
    detector = MovementDetector(settings, CAMERA_ID)
    position_history = []
    fps_regulator = FpsRegulator(FPS)
    try:
        while True:
            fps_regulator.wait_until_next_frame()

            _, object_positions = detector.detect_movement()
            capture_time = fps_regulator.current_frame_time_ns()
            position_history.append((capture_time, object_positions))
            show_preview(detector.get_previous_frame(), object_positions)
            key = cv.waitKey(1)

            if key == ord("q"):
                break
    except KeyboardInterrupt:
        print("Keyboard interrupt")

    # Write the positions to a CSV file
    with open("positions.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["time", "x", "y"])
        for t, positions in position_history:
            for x, y in positions:
                writer.writerow([t, x, y])

    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
    # Main can also be run in a separate thread, like this:
    # ```
    # from threading import Thread
    # t = Thread(target=main)
    # t.start()
    # ```
    # Using mulpiprocessing instead results in OpenCV not being able to take
    # control of the camera, which renders the program useless.
