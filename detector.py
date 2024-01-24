#!/usr/bin/env python3
import cv2 as cv
import time
import csv
from movement_detector import MovementDetector, Settings

CAMERA_ID = 0
FPS = 6


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


def main():
    detector = MovementDetector(Settings(15, 20, 15), CAMERA_ID)
    position_history = []
    while True:
        try:
            t = time.time()

            capture_time, object_positions = detector.detect_movement()
            position_history.append((capture_time, object_positions))
            show_preview(detector.get_previous_frame(), object_positions)
            key = cv.waitKey(1)

            time_taken = time.time() - t

            to_sleep = (1 / FPS) - time_taken

            if to_sleep <= 0:
                print(f"Lagging behind by {-to_sleep}!")
                print(f"Time taken: {time_taken}")
            else:
                time.sleep(to_sleep)

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

    cv.destroyAllWindows()


if __name__ == "__main__":
    from threading import Thread

    t = Thread(target=main)
    t.start()
    time.sleep(1000000)
