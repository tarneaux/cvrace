# Demonstrate motion position detection using OpenCV
# Write images to output/ at each step

import cv2 as cv
import numpy as np
import os

# Create output/ directory if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

im1 = cv.imread('im1.png')
im2 = cv.imread('im2.png')

# Write images to output/
cv.imwrite('output/1_im1.png', im1)
cv.imwrite('output/1_im2.png', im2)

# Convert images to grayscale
im1_gray = cv.cvtColor(im1, cv.COLOR_BGR2GRAY)
im2_gray = cv.cvtColor(im2, cv.COLOR_BGR2GRAY)

# Write images to output/
cv.imwrite('output/2_im1_gray.png', im1_gray)
cv.imwrite('output/2_im2_gray.png', im2_gray)

# Compute the difference between the two images
diff = cv.absdiff(im1_gray, im2_gray)

# Write images to output/
cv.imwrite('output/3_diff.png', diff)

# Blur the difference to reduce noise
blurred = cv.GaussianBlur(diff, (15, 15), 0)

cv.imwrite('output/4_blurred.png', blurred)

# Threshold the difference to create a binary image
_, thresh = cv.threshold(blurred, 10, 255, cv.THRESH_BINARY)
cv.imwrite('output/5_thresh.png', thresh)

# Dilate the thresholded image to link contours
dilated = cv.dilate(thresh, None, iterations=15)
cv.imwrite('output/6_dilated.png', dilated)

# Find contours in the dilated image
contours, _ = cv.findContours(dilated, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

# Draw contours on a blank image
black = np.zeros_like(im1)
cv.drawContours(black, contours, -1, (0, 255, 0), 3)
cv.imwrite('output/7_contours.png', black)

# Find contour centers
centers = []
for contour in contours:
    M = cv.moments(contour)
    if M['m00'] != 0:
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
        centers.append(center)

# Draw centers on the black image
black = np.zeros_like(im1)
for center in centers:
    cv.circle(black, center, 5, (0, 0, 255), -1)
cv.imwrite('output/8_centers.png', black)

# Draw centers on the original image
for center in centers:
    cv.circle(im1, center, 5, (0, 0, 255), -1)
cv.imwrite('output/9_im1_centers.png', im1)
