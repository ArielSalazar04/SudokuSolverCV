import cv2
import imutils
import numpy as np
from math import dist
from tensorflow.keras.models import load_model
from keras_preprocessing.image import img_to_array
from skimage.segmentation import clear_border


class PuzzleFinder:
    __image = None
    __cannyImage = None
    __gridCorners = None
    __puzzleImage = None
    __digitReader = None

    def __init__(self, img):
        self.updateImage(img)
        self.__digitReader = load_model("model/digitReader.h5")

    def updateImage(self, image):
        self.__image = image
        self.__preprocessImage()

    def __preprocessImage(self):
        imgGray = cv2.cvtColor(self.__image, cv2.COLOR_BGR2GRAY)
        imgBlurred = cv2.GaussianBlur(imgGray, (5, 5), 3)
        self.__cannyImage = cv2.Canny(imgBlurred, 50, 50)

    def getGridContour(self):
        contours, hierarchy = cv2.findContours(self.__cannyImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        minOutline, maxOutline = 360000, 450000
        minArea, maxArea = 400000, 420000

        # find grid contour
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if minOutline <= area <= maxOutline:
                # Find coordinates of contour corners
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.05 * perimeter, True)

                # Drawing skewed rectangle and corners
                cv2.drawContours(self.__image, [approx], -1, (0, 255, 0), 4)
                for point in approx:
                    x, y = point[0]
                    cv2.circle(self.__image, (x, y), 4, (0, 0, 255), 8)

                # Sudoku grid has been detected
                if minArea <= area <= maxArea:
                    self.__gridCorners = approx.reshape((4, 2))
                    return True

        self.__gridCorners = None
        return False

    def extractGridFromContour(self):
        # Classify each point as top/bottom and left/right
        sortedCoordinates = self.__gridCorners[self.__gridCorners[:, 0].argsort()]
        leftSide = sortedCoordinates[:2]
        rightSide = sortedCoordinates[2:]
        topLeft, bottomLeft = leftSide[leftSide[:, 1].argsort()]
        topRight, bottomRight = rightSide[rightSide[:, 1].argsort()]
        topLeft = [topLeft[0] + 4, topLeft[1] + 4]
        topRight = [topRight[0] - 4, topRight[1] + 4]
        bottomLeft = [bottomLeft[0] + 4, bottomLeft[1] - 4]
        bottomRight = [bottomRight[0] - 4, bottomRight[1] - 4]

        # Find the max width and height of the grid
        heightLeft = dist(topLeft, bottomLeft)
        heightRight = dist(topRight, bottomRight)
        maxHeight = max(int(heightLeft), int(heightRight))
        widthTop = dist(topLeft, topRight)
        widthBottom = dist(bottomLeft, bottomRight)
        maxWidth = max(int(widthTop), int(widthBottom))

        # Warp the image
        inputPts = np.float32([topLeft, bottomLeft, bottomRight, topRight])
        outputPts = np.float32([[0, 0], [0, maxHeight - 1], [maxWidth - 1, maxHeight - 1], [maxWidth - 1, 0]])
        M = cv2.getPerspectiveTransform(inputPts, outputPts)
        warpedGrid = cv2.warpPerspective(self.__image, M, (maxWidth, maxHeight), flags=cv2.INTER_LINEAR)

        # Preprocess image before analyzing squares
        grayscaleGrid = cv2.cvtColor(warpedGrid, cv2.COLOR_BGR2GRAY)
        threshGrid = cv2.threshold(grayscaleGrid, 127, 255, cv2.THRESH_BINARY)[1]
        self.__puzzleImage = cv2.resize(threshGrid, (450, 450), interpolation=cv2.INTER_AREA)

    def analyzeSquares(self):
        puzzle = np.zeros((9, 9)).astype(int)
        newCoordinates = set()

        for y in range(0, 401, 50):
            for x in range(0, 401, 50):
                square = self.__puzzleImage[y:y + 50, x:x + 50]

                # Determine if digit contains a digit or not
                digit = self.__extractDigit(square)
                prediction = 0

                # If digit exists, predict it
                if digit is not None:
                    squareSample = cv2.resize(digit, (28, 28))
                    squareSample = squareSample.astype("float") / 255.0
                    squareSample = img_to_array(squareSample)
                    squareSample = np.expand_dims(squareSample, axis=0)
                    prediction = int(self.__digitReader.predict(squareSample).argmax(axis=1)[0])
                else:
                    newCoordinates.add((y // 50, x // 50))

                puzzle[y // 50, x // 50] = prediction

        return puzzle, newCoordinates

    def __extractDigit(self, cell):
        thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        thresh = clear_border(thresh)

        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        if len(cnts) == 0:
            return None

        c = max(cnts, key=cv2.contourArea)
        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)

        (h, w) = thresh.shape

        percentFilled = cv2.countNonZero(mask) / float(h * w)

        if percentFilled < 0.03:
            return None

        digit = cv2.bitwise_and(thresh, thresh, mask=mask)

        return digit
