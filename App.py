import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from PuzzleFinder import PuzzleFinder
from SudokuSolver import SudokuSolver
from tensorflow.keras.models import load_model


class App:
    # Main window widgets & data
    __mainWindow = None
    __webcamButton = None
    __uploadButton = None
    __clearButton = None
    __grid = None
    __tutorialButton = None
    __cells = None
    __intVars = None

    # Webcam window widgets
    __webcamWindow = None
    __webcamLabel = None
    __vc = None
    __digitReader = None

    # Upload window widgets & data
    __uploadWindow = None
    __uploadImageLabel = None
    __uploadBackButton = None
    __uploadNextButton = None
    __uploadApproveButton = None
    __uploadCurrentImage = None
    __uploadContourList = None
    __uploadPageIndex = 0
    __uploadContourSize = 0

    # Tutorial window widgets
    __tutorialWindow = None
    __tutorialImage = None
    __tutorialSubtitle = None
    __tutorialTextVar = None
    __backButton = None
    __nextButton = None
    __images = None
    __subtitles = None
    __numPages = 7
    __pageIndex = 0

    # Helper Classes
    __puzzleFinder = None
    __sudokuSolver = None

    # Colors
    LIGHT_RED = "#ff6363"
    LIGHT_GREEN = "#63ff78"
    WHITE = "#ffffff"
    BACKGROUND_COLOR = "light gray"

    def __init__(self):
        # Load digit reader
        self.__digitReader = load_model("model/digitReader.h5")

        # Create GUI main window
        self.__mainWindow = tk.Tk()
        self.__mainWindow.title("Sudoku Solver CV")
        self.__mainWindow.geometry("%dx%d+%d+%d" % (540, 540, 50, 50))
        self.__mainWindow.resizable(False, False)
        self.__mainWindow.configure(background=self.BACKGROUND_COLOR)
        self.__mainWindow.bind('<Escape>', lambda m: self.__killMainWin())
        self.__mainWindow.protocol("WM_DELETE_WINDOW", self.__killMainWin)

        # Create Grid
        step = 2
        self.__grid = tk.Canvas(self.__mainWindow)
        self.__grid.configure(background=self.BACKGROUND_COLOR)
        self.__grid["highlightthickness"] = 0
        self.__grid.place(relx=0.5, rely=0.4, anchor=tk.CENTER, width=360-step, height=360-step)

        self.__cells = np.empty((9, 9)).astype(tk.Entry)
        self.__intVars = np.empty((9, 9)).astype(tk.IntVar)

        # Draw grid lines for 3x3 squares
        self.__grid.create_line(120, 0, 120, 360 - step, fill="black", width=2*step)
        self.__grid.create_line(240, 0, 240, 360 - step, fill="black", width=2*step)
        self.__grid.create_line(0, 120, 360 - step, 120, fill="black", width=2*step)
        self.__grid.create_line(0, 240, 360 - step, 240, fill="black", width=2*step)

        for i in range(0, 360, 40):
            for j in range(0, 360, 40):
                var = tk.IntVar()
                var.set("")
                cell = tk.Entry(self.__grid)
                cell["font"] = "Helvetica 16 bold"
                cell['bg'] = "white"
                cell['fg'] = "black"
                cell["justify"] = tk.CENTER
                cell["highlightthickness"] = 0
                cell["textvariable"] = var
                cell.place(width=40-step, height=40-step, x=j, y=i)
                self.__cells[i // 40, j // 40] = cell
                self.__intVars[i // 40, j // 40] = var

        # Webcam Enable Button
        self.__webcamButton = tk.Button(self.__mainWindow, command=self.__enableWebcam)
        self.__webcamButton["text"] = "Launch Webcam"
        self.__webcamButton["font"] = "Helvetica 12 bold"
        self.__webcamButton["highlightthickness"] = 0
        self.__webcamButton.place(width=154, height=36, relx=0.35, rely=0.80, anchor=tk.CENTER)

        # Upload Image Button
        self.__uploadButton = tk.Button(self.__mainWindow, command=self.__uploadImage)
        self.__uploadButton["text"] = "Upload Image"
        self.__uploadButton["font"] = "Helvetica 12 bold"
        self.__uploadButton["highlightthickness"] = 0
        self.__uploadButton.place(width=154, height=36, relx=0.65, rely=0.80, anchor=tk.CENTER)

        # Upload Image Lists
        self.__uploadContourList = []

        # Clear Button
        self.__clearButton = tk.Button(self.__mainWindow, command=self.__clearGrid)
        self.__clearButton["text"] = "Clear Grid"
        self.__clearButton["font"] = "Helvetica 12 bold"
        self.__clearButton["highlightthickness"] = 0
        self.__clearButton.place(width=154, height=36, relx=0.5, rely=0.90, anchor=tk.CENTER)

        # Tutorial Button
        self.__tutorialButton = tk.Button(self.__mainWindow, command=self.__showInfo)
        self.__tutorialButton["text"] = "i"
        self.__tutorialButton["font"] = "Courier 12 bold"
        self.__tutorialButton["highlightthickness"] = 0
        self.__tutorialButton.place(width=36, height=36, relx=0.9, rely=0.90, anchor=tk.CENTER)

        # Tutorial Data
        self.__images = [None] * self.__numPages
        self.__subtitles = [""] * self.__numPages

        self.__images[0] = cv2.imread("images/image1.png")
        self.__images[1] = cv2.imread("images/image2.png")
        self.__images[2] = cv2.imread("images/image3.png")
        self.__images[3] = cv2.imread("images/image4.png")
        self.__images[4] = cv2.imread("images/image5.png")
        self.__images[5] = cv2.imread("images/image6.png")
        self.__images[6] = cv2.imread("images/image7.png")

        self.__subtitles[0] = "1. Click on 'Launch Webcam' to open the webcam for\nreading an unsolved Sudoku puzzle."
        self.__subtitles[1] = "2. Hold up the Sudoku puzzle in front of the webcam."
        self.__subtitles[2] = "3. Move the Sudoku puzzle closer when prompted to."
        self.__subtitles[3] = "4. Move the Sudoku puzzle further when prompted to."
        self.__subtitles[4] = "5. Stop moving tbe puzzle when prompted to."
        self.__subtitles[5] = "6. The red cells make up the illegal constraints\nof the puzzle."
        self.__subtitles[6] = "7. The white cells make up the current state, \nthe green cells make up the solution."

        self.__tutorialTextVar = tk.StringVar()

        # Launch the Tkinter GUI
        self.__mainWindow.mainloop()

    def __updateGrid(self, sudokuGrid, newCoordinates):
        for i in range(9):
            for j in range(9):
                self.__intVars[i, j].set(sudokuGrid[i, j])
                self.__cells[i, j]["bg"] = self.LIGHT_GREEN if (i, j) in newCoordinates else self.WHITE

    def __showIllegalGrid(self, sudokuGrid, conflicts):
        for i in range(9):
            for j in range(9):
                if not sudokuGrid[i, j] == 0:
                    self.__intVars[i, j].set(sudokuGrid[i, j])
                    self.__cells[i, j]["bg"] = self.LIGHT_RED if (i, j) in conflicts else self.WHITE

    def __clearGrid(self):
        for i in range(9):
            for j in range(9):
                self.__intVars[i, j].set("")
                self.__cells[i, j]['bg'] = "white"

    def __killMainWin(self):
        # destroy the main window
        self.__mainWindow.destroy()
        self.__mainWindow.quit()

    def __killWebcamWin(self):
        # reactivate buttons on main window
        self.__toggleMainMenuButtons("normal")

        # destroy the webcam window
        self.__webcamWin.destroy()
        self.__webcamWin.quit()
        self.__vc.release()

    def __killUploadWin(self):
        # reactivate buttons on main window
        self.__toggleMainMenuButtons("normal")

        # reset upload window data members to default values
        self.__uploadContourList.clear()
        self.__uploadCurrentImage = None
        self.__uploadPageIndex = 0
        self.__uploadContourSize = 0

        # destroy the upload window
        self.__uploadWindow.destroy()

    def __killTutorialWin(self):
        # reactivate buttons on main window
        self.__toggleMainMenuButtons("normal")

        # destroy the tutorial window
        self.__tutorialWindow.destroy()
        self.__tutorialWindow.quit()

    def __approve(self):
        # update contour that will be used to extract the grid, if possible
        success = self.__puzzleFinder.setContour(self.__uploadContourList[self.__uploadPageIndex])
        if not success:
            self.__showGridNotFoundError()
            return None

        # extract the grid from the image and solve the puzzle
        self.__extractAndSolve()

    def __enableWebcam(self):
        # Create the webcam
        self.__vc = cv2.VideoCapture(0)
        width, height = self.__vc.get(cv2.CAP_PROP_FRAME_WIDTH), self.__vc.get(cv2.CAP_PROP_FRAME_HEIGHT)

        success, img = self.__vc.read()
        if success:
            # Disable webcam button
            self.__webcamButton["state"] = "disable"

            # Create a child window that will contain the webcam video
            x, y = self.__mainWindow.winfo_x(), self.__mainWindow.winfo_y()
            self.__webcamWin = tk.Toplevel(self.__mainWindow)
            self.__webcamWin.geometry("%dx%d+%d+%d" % (width, height, x + 600, y))
            self.__webcamWin.resizable(False, False)
            self.__webcamWin.configure(background=self.BACKGROUND_COLOR)
            self.__webcamWin.bind('<Escape>', lambda w: self.__killWebcamWin())
            self.__webcamWin.protocol("WM_DELETE_WINDOW", self.__killWebcamWin)
            self.__webcamLabel = tk.Label(self.__webcamWin)
            self.__webcamLabel.pack()

            self.__puzzleFinder = PuzzleFinder(img, self.__digitReader)
            self.__sudokuSolver = SudokuSolver()
            self.__showFrame()
            self.__webcamWin.mainloop()

        else:
            self.__vc.release()
            self.__showWebcamError()

    def __showFrame(self):
        # Read and preprocess frame
        success, img = self.__vc.read()
        if not success:
            self.__killWebcamWin()
            self.__showWebcamError()
            return None

        # Get grid contour (if none is found, continue to next frame)
        self.__puzzleFinder.updateImage(img)
        hasGrid = self.__puzzleFinder.getGridCornersWeb()

        # If contour is found, extract the puzzle from the image and solve the puzzle
        if hasGrid:
            # Extract puzzle and solve it
            self.__puzzleFinder.extractGridFromCorners()
            sudokuPuzzle, blankSquares = self.__puzzleFinder.analyzeSquares()

            # Solve the puzzle only if all constraints are met
            if self.__sudokuSolver.isValidPuzzle(sudokuPuzzle):
                self.__sudokuSolver.setGrid(sudokuPuzzle)
                if self.__sudokuSolver.solveSudoku():
                    self.__clearGrid()
                    self.__updateGrid(sudokuPuzzle, blankSquares)
                else:
                    conflicts = self.__sudokuSolver.getAllConflicts(sudokuPuzzle)
                    self.__clearGrid()
                    self.__showIllegalGrid(sudokuPuzzle, conflicts)
            else:
                conflicts = self.__sudokuSolver.getAllConflicts(sudokuPuzzle)
                self.__clearGrid()
                self.__showIllegalGrid(sudokuPuzzle, conflicts)

        # Display next image onto webcam window
        cv2Img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        webcamImg = Image.fromarray(cv2Img)
        imgtk = ImageTk.PhotoImage(image=webcamImg)
        self.__webcamLabel.imgtk = imgtk
        self.__webcamLabel.configure(image=imgtk)
        self.__webcamLabel.after(10, self.__showFrame)

    def __uploadImage(self):
        # ask the user for an image file
        filePath = filedialog.askopenfilename()

        # if image file was not selected, stop
        if not filePath:
            return None

        # disable all buttons on main window
        self.__toggleMainMenuButtons("disabled")

        # if image file does not have an appropriate file extension, stop
        if not filePath.endswith((".png", ".jpg", "jpeg")):
            self.__showFileExtensionError()
            return None

        # read the image from the file path
        self.__uploadCurrentImage = cv2.imread(filePath)
        if self.__uploadCurrentImage is None:
            self.__showImageFileNotReadError()
            return None

        # get the grid contour and vertices
        self.__puzzleFinder = PuzzleFinder(self.__uploadCurrentImage, self.__digitReader)
        self.__sudokuSolver = SudokuSolver()
        contours = self.__puzzleFinder.getGridContours()

        # if no contours were calculated, stop
        if contours is None:
            self.__showNoContoursError()
            return None

        # sort contours by largest area to smallest
        self.__uploadContourList = sorted(contours, key=cv2.contourArea, reverse=True)
        self.__uploadContourSize = int(cv2.contourArea(self.__uploadContourList[0]) // 14e4)

        # open the upload window
        x, y = self.__mainWindow.winfo_x(), self.__mainWindow.winfo_y()
        self.__uploadWindow = tk.Toplevel(self.__mainWindow)
        self.__uploadWindow.geometry("%dx%d+%d+%d" % (580, 640, x + 600, y))
        self.__uploadWindow.resizable(False, False)
        self.__uploadWindow.configure(background=self.BACKGROUND_COLOR)
        self.__uploadWindow.bind('<Escape>', lambda w: self.__killUploadWin())
        self.__uploadWindow.protocol("WM_DELETE_WINDOW", self.__killUploadWin)

        self.__uploadBackButton = tk.Button(self.__uploadWindow, command=self.__uploadBackPage)
        self.__uploadBackButton["text"] = "Back"
        self.__uploadBackButton["font"] = "Helvetica 12 bold"
        self.__uploadBackButton["state"] = "disable"
        self.__uploadBackButton["highlightthickness"] = 0
        self.__uploadBackButton.place(width=60, height=28, relx=0.05, rely=0.925)

        self.__uploadNextButton = tk.Button(self.__uploadWindow, command=self.__uploadNextPage)
        self.__uploadNextButton["text"] = "Next"
        self.__uploadNextButton["font"] = "Helvetica 12 bold"
        self.__uploadNextButton["highlightthickness"] = 0
        self.__uploadNextButton.place(width=60, height=28, relx=0.85, rely=0.925)

        self.__uploadApproveButton = tk.Button(self.__uploadWindow, command=lambda: self.__approve())
        self.__uploadApproveButton["text"] = "Approve"
        self.__uploadApproveButton["font"] = "Helvetica 12 bold"
        self.__uploadApproveButton["highlightthickness"] = 0
        self.__uploadApproveButton.place(width=90, height=28, relx=0.425, rely=0.925)

        self.__uploadLabel = tk.Label(self.__uploadWindow, borderwidth=4, relief="solid")
        self.__uploadLabel.pack(anchor="n", pady=8)

        # display the first image with contour on the upload window
        self.__uploadUpdateImages(self.__uploadPageIndex)

    def __uploadUpdateImages(self, index):
        # get an approximation of the contour
        cnt = self.__uploadContourList[index]
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * perimeter, True)

        # copy the current image
        newImg = self.__uploadCurrentImage.copy()

        # draw contour and corners on image
        cv2.cvtColor(newImg, cv2.COLOR_BGR2RGBA)
        cv2.drawContours(newImg, [approx], -1, (0, 255, 0), self.__uploadContourSize)
        for point in approx:
            cv2.circle(newImg, point[0], self.__uploadContourSize, (0, 0, 255), self.__uploadContourSize)

        # resize the image
        newWidth = int(self.__uploadCurrentImage.shape[1] * 540 / self.__uploadCurrentImage.shape[0])
        newImg = cv2.resize(newImg, (newWidth, 540), interpolation=cv2.INTER_AREA)

        # display image
        webcamImg = Image.fromarray(newImg)
        imgtk = ImageTk.PhotoImage(webcamImg)
        self.__uploadLabel.configure(image=imgtk)
        self.__uploadLabel.image = imgtk

    def __uploadNextPage(self):
        if self.__uploadPageIndex == 0:
            self.__uploadBackButton["state"] = "normal"
        self.__uploadPageIndex += 1
        self.__uploadUpdateImages(self.__uploadPageIndex)
        if self.__uploadPageIndex == len(self.__uploadContourList)-1:
            self.__uploadNextButton["state"] = "disable"

    def __uploadBackPage(self):
        if self.__uploadPageIndex == len(self.__uploadContourList)-1:
            self.__uploadNextButton["state"] = "normal"
        self.__uploadPageIndex -= 1
        self.__uploadUpdateImages(self.__uploadPageIndex)
        if self.__uploadPageIndex == 0:
            self.__uploadBackButton["state"] = "disable"

    def __toggleMainMenuButtons(self, state):
        self.__webcamButton["state"] = state
        self.__uploadButton["state"] = state
        self.__clearButton["state"] = state
        self.__tutorialButton["state"] = state

    def __extractAndSolve(self):
        # Extract puzzle and solve it
        self.__puzzleFinder.extractGridFromCorners()
        sudokuPuzzle, blankSquares = self.__puzzleFinder.analyzeSquares()

        # Solve the puzzle only if all constraints are met
        if self.__sudokuSolver.isValidPuzzle(sudokuPuzzle):
            self.__sudokuSolver.setGrid(sudokuPuzzle)
            if self.__sudokuSolver.solveSudoku():
                self.__clearGrid()
                self.__updateGrid(sudokuPuzzle, blankSquares)
            else:
                self.__impossiblePuzzleError()
        else:
            conflicts = self.__sudokuSolver.getAllConflicts(sudokuPuzzle)
            self.__clearGrid()
            self.__showIllegalGrid(sudokuPuzzle, conflicts)
            self.__showIllegalConstraintsError()

    def __showInfo(self):
        # Create a child window that will contain the tutorial
        x, y = self.__mainWindow.winfo_x(), self.__mainWindow.winfo_y()
        self.__tutorialWindow = tk.Toplevel(self.__mainWindow)
        self.__tutorialWindow.title("Sudoku Solver CV Tutorial")
        self.__tutorialWindow.geometry("1020x840+%d+%d" % (x + 600, y))
        self.__tutorialWindow.resizable(False, False)
        self.__tutorialWindow.configure(background=self.BACKGROUND_COLOR)
        self.__tutorialWindow.bind('<Escape>', lambda w: self.__killTutorialWin())
        self.__tutorialWindow.protocol("WM_DELETE_WINDOW", self.__killTutorialWin)

        # Assign first image and subtitle to tutorial window
        self.__tutorialImage = tk.Label(self.__tutorialWindow)
        self.__tutorialImage.pack(side="top")
        self.__tutorialSubtitle = tk.Label(self.__tutorialWindow, textvariable=self.__tutorialTextVar, height=2)
        self.__tutorialSubtitle.configure(fg="black")
        self.__tutorialSubtitle.configure(bg=self.BACKGROUND_COLOR)
        self.__tutorialSubtitle.place(relx=0.325, rely=0.925)
        self.__pageIndex = 0
        self.__updatePage(self.__pageIndex)

        # Back and Next button
        self.__backButton = tk.Button(self.__tutorialWindow, command=self.__backPage)
        self.__backButton["text"] = "Back"
        self.__backButton["font"] = "Helvetica 12 bold"
        self.__backButton["state"] = "disable"
        self.__backButton["highlightthickness"] = 0
        self.__backButton.place(width=60, height=28, relx=0.025, rely=0.925)

        self.__nextButton = tk.Button(self.__tutorialWindow, command=self.__nextPage)
        self.__nextButton["text"] = "Next"
        self.__nextButton["font"] = "Helvetica 12 bold"
        self.__nextButton["highlightthickness"] = 0
        self.__nextButton.place(width=60, height=28, relx=0.925, rely=0.925)

        self.__tutorialWindow.mainloop()

    def __updatePage(self, index):
        img = self.__images[index]
        cv2Img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        tutorialImg = Image.fromarray(cv2Img)
        tutorialTk = ImageTk.PhotoImage(image=tutorialImg)
        self.__tutorialImage.imgtk = tutorialTk
        self.__tutorialImage.configure(image=tutorialTk)
        self.__tutorialTextVar.set(self.__subtitles[index])

    def __nextPage(self):
        if self.__pageIndex == 0:
            self.__backButton["state"] = "normal"
        self.__pageIndex += 1
        self.__updatePage(self.__pageIndex)
        if self.__pageIndex == self.__numPages-1:
            self.__nextButton["state"] = "disable"

    def __backPage(self):
        if self.__pageIndex == self.__numPages-1:
            self.__nextButton["state"] = "normal"
        self.__pageIndex -= 1
        self.__updatePage(self.__pageIndex)
        if self.__pageIndex == 0:
            self.__backButton["state"] = "disable"

    @staticmethod
    def __showWebcamError():
        messagebox.showerror("Error", "Webcam did not open successfully.")

    @staticmethod
    def __showFileExtensionError():
        messagebox.showerror("Error", "File must have a .png, .jpg, or .jpeg extension.")

    @staticmethod
    def __showImageFileNotReadError():
        messagebox.showerror("Error", "Image file uploaded could not be read.")
    @staticmethod
    def __showNoContoursError():
        messagebox.showerror("Error", "No contours were found in the image.")

    @staticmethod
    def __showGridNotFoundError():
        messagebox.showerror("Error", "Grid was not found in the image.")

    @staticmethod
    def __showIllegalConstraintsError():
        messagebox.showerror("Error", "Detected puzzle has invalid constraints or was not read properly.")

    @staticmethod
    def __impossiblePuzzleError():
        messagebox.showerror("Error", "Puzzle is impossible to solve.")

