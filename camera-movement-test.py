#!/usr/bin/env python3

# Take pictures with a 1s interval.
# For each picture, make a new picture which is the difference between the current and previous picture.

import cv2 as cv
import numpy as n
from picamera2 import Picamera2
from time import sleep, time

# Threshold for the difference between two consecutive values of a pixel to be considered a change
DIFFTOZERO = 5

picam = Picamera2()
# picam2.configure(picam2.create_still_configuration({"size":(4056, 3040)})) # Slows down
picam.start(show_preview=False)

prevImg = None
prevtime = None

# interval between pictures in seconds
INTERVAL = 0.1

while True:
    prevtime = time()
    # Take a picture
    img = picam.capture_array()

    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # imgGray = cv.resize(imgGray, (507, 380))

    if prevImg is not None:
        imgDiff = imgGray - prevImg + 127
        # All differences with a value < 127
        imgNeg = n.where(imgDiff < 127, imgDiff, 127)
        # All differences with a value > 127
        imgPos = n.where(imgDiff > 127, imgDiff, 127)
    
        try:
            # Find the mean X and Y of all points which have a positive value
            # (i.e. the mean of all points which are different from the previous picture)
            meanXpos = n.mean(n.where(imgPos > 127+DIFFTOZERO)[1]) # TODO: coefficient based on the value of the difference between the two pictures

            meanYpos = n.mean(n.where(imgPos > 127+DIFFTOZERO)[0])
            print(f"Mean X: {meanXpos}, Mean Y: {meanYpos}")

            # Draw a green circle at the mean X and Y
            cv.circle(imgDiff, (int(meanXpos), int(meanYpos)), 10, (0, 0, 0), 2)

            # Find the mean X and Y of all points which have a negative value
            # (i.e. the mean of all points which are the same as the previous picture)
            meanXneg = n.mean(n.where(imgNeg < 127-DIFFTOZERO)[1])
            meanYneg = n.mean(n.where(imgNeg < 127-DIFFTOZERO)[0])
            print(f"Mean X: {meanXneg}, Mean Y: {meanYneg}")

            # Draw a circle at the mean X and Y
            cv.circle(imgDiff, (int(meanXneg), int(meanYneg)), 10, (255, 255, 255), 2)

            # Draw an X at the mean of those two points
            meanmeanX = (meanXpos + meanXneg) / 2
            meanmeanY = (meanYpos + meanYneg) / 2
            cv.line(imgDiff, (int(meanmeanX) - 10, int(meanmeanY) - 10), (int(meanmeanX) + 10, int(meanmeanY) + 10), (0, 0, 0), 2)
            cv.line(imgDiff, (int(meanmeanX) - 10, int(meanmeanY) + 10), (int(meanmeanX) + 10, int(meanmeanY) - 10), (0, 0, 0), 2)
        except ValueError:
            pass

        cv.imshow("diff", imgDiff)
    else:
        cv.imshow("diff", imgGray)

    prevImg = imgGray

    print("Picture taken")
    if prevtime is not None:
        print("Time since start of this iteration: " + str(time() - prevtime))
        tosleep = prevtime + INTERVAL - time()
        if tosleep > 0:
            print(f"Time to wait to complete {INTERVAL}s interval: {tosleep}")
            cv.waitKey(int(tosleep * 1000))
