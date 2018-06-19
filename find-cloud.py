#!/usr/bin/env python
from __future__ import division
import sys, cv2, pylab
import numpy as np

#--------------------------------------------------------------------------------
#The aim of this application is to scan an image for clouds and mask them yellow.
#The application achieves this using an algorithms that finds colours within specific
#ranges and masks them a white colour while all other elements of the image are removed
#The mask is then merged with the original image in an overlay and painted yellow to show the sections of the
#clouds that have been replaced.

#The original image and the masked image are then placed side by side to show the
#user the results of the image masking.

#Overall I am happy with the results as it seems to work well on most photos with
#acceptable light levels finding most of the clouds in the image.

#I wish I could have implemented some further tweaking to remove some graphical glitches
#between the different mask layers and also for images with darker light levels.
#---------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# Masking funcitons Convert to mask and Blend masks
# -------------------------------------------------------------------------------

def iround(x):
    return int(round(x))


def mean(im):
    # Calculates the mean of the image im.
    ny, nx, nc = im.shape
    total = 0
    for y in range(0, ny):
        for x in range(0, nx):
            for c in range(0, nc):
                total += im[y, x, c]
    return total / ny / nx / nc


def convert(im, std):
    # Converts the image into a series of masks that mask certain colour ranges and make them white

    dark_grey = np.array([60, 60, 60], dtype="uint16")  # these are the colour ranges i'm using to mask the clouds
    medium_grey = np.array([100, 120, 120], dtype="uint16")
    light_grey = np.array([150, 150, 150], dtype="uint16")
    white = np.array([255, 255, 255], dtype="uint16")
    # im = cv2.GaussianBlur(im, (5,5),0)
    # im = cv2.bilateralFilter(im,9,75,75)

    mask = cv2.inRange(im, light_grey, white)
    mask2 = cv2.inRange(im, medium_grey, light_grey)
    mask3 = cv2.inRange(im, dark_grey, medium_grey)
    return mask2, mask3, mask


def blend(im):
    co = im.copy()  # creates a copy of the image to be edited

    # Turns masks back into RGB images and blends them together and then turns the mask yellow
    # The masks are then blended on top of the original image which highlights clouds
    (a, b, c) = convert(im, im.std())
    overlay1 = cv2.cvtColor(a, cv2.COLOR_GRAY2BGR)
    overlay2 = cv2.cvtColor(b, cv2.COLOR_GRAY2BGR)
    overlay3 = cv2.cvtColor(c, cv2.COLOR_GRAY2BGR)

    co[np.where((overlay1 == [255, 255, 255]).all(axis=2))] = [0, 255, 255]  # coverts overlay 1 to yellow
    co[np.where((overlay2 == [255, 255, 255]).all(axis=2))] = [0, 255, 255]  # converts overlay 2 to yellow
    co[np.where((overlay3 == [255, 255, 255]).all(axis=2))] = [0, 255, 255]  # converts overlay 3 to yellow

    # dst = cv2.addWeighted(im, 0.9, overlay1, 1, 0)
    # dst2 = cv2.addWeighted(dst, 1, overlay2, 1, 0)
    # dst3 = cv2.addWeighted(dst2, 1, overlay3, 1, 0)


    return co


# -------------------------------------------------------------------------------
# Main program.
# -------------------------------------------------------------------------------
# Sets up maximum display
maxdisp = 800

# Takes command line argument and checks if appropriate
if len(sys.argv) < 2:
    print >> sys.stderr, "Usage:", sys.argv[0], "<image>..."
    sys.exit(1)

# Takes command line arguemnt.
for fn in sys.argv[1:]:
    # Takes image and outputs dimensions.
    im = cv2.imread(fn)  # attempts to open a file with the same name from the command line argument
    ny, nx, nc = im.shape  # sets the images pixel count to NX, the lines to NC, and the chanels to NC
    print fn + ":"
    print "  Dimensions:", nx, "pixels,", ny, "lines,", nc, "channels."  # prints out the images pixel count,line count, and chanels.

    # Calculates statistics about the image, the mean and the standard deviation.
    print "  Range: %d to %d" % (im.min(), im.max())  # gets the colour range of the image (Should always be 0 to 255)
    print "  Mean: %.2f (using mean)" % mean(im)  # prints the mean to 2 decimal places
    print "  Mean: %.2f (using numpy method)" % im.mean()  # prints the mean using numpy inbuilt mean function to 2 decimal places
    print "  Standard deviation: %.2f" % im.std()  # gets the standard deviation of the image to 2 decimal places

    # Constrains image resolution to 800 by 800.
    if ny > maxdisp or nx > maxdisp:  # if the image is larger than 800 by 800
        nmax = max(ny, nx)  # it will set the the height and the width (lines and pixel count) to 800
        fac = maxdisp / nmax
        nny = iround(ny * fac)
        nnx = iround(nx * fac)
        print "  [re-sizing to %d x %d pixels for display]" % (nnx, nny)
        im = cv2.resize(im, (nnx, nny))

    # Displays the image.
    newIm = blend(im)  # creates the mask of the image
    aa = np.hstack((im, newIm))  # puts original image and masked image side by side
    cv2.imshow(fn, aa)  # shows the image stack

    cv2.waitKey(0)
    cv2.destroyWindow(fn)
    print

# I had some issues with masks overlapping and cancelling each other out, for some reason it deletes some of the mask where it overlaps, even if it's in range

# Also, if the sky has a heavy gradient (Eg. sunset) the mask doesn't work as it grabs the gradient of the sunset along with the clouds.
