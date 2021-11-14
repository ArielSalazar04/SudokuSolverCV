import cv2


class PuzzleFinder:
    __image = None
    __cannyImage = None

    def __init__(self, img):
        self.updateImage(img)

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
                cv2.drawContours(self.__image, cnt, -1, (0, 255, 0), 2)
                if minArea <= area <= maxArea:  # Sudoku grid has been detected
                    return cnt

        return None

    def extractGridFromContour(self):
        pass

    def analyzeSquares(self):
        pass

    def __extractDigit(self):
        pass
