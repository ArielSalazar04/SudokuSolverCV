import cv2

vc = cv2.VideoCapture(0)

while True:
    # Read a frame
    success, img = vc.read()

    # Show the frame on preview
    cv2.imshow("Sudoku Solver with Computer Vision", img)

    # Break loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xff == ord('q'):  # exit on q
        cv2.destroyAllWindows()
        break
