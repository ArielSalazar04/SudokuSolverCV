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

    # Tutorial window widgets
    __tutorialWindow = None
    __tutorialImage = None
    __tutorialSubtitle = None
    __tutorialTextVar = None
    __backButton = None
    __nextButton = None
    __images = None
    __subtitles = None
    __numPages = 6
    __pageIndex = 0

    # Helper Classes
    __puzzleFinder = None
    __sudokuSolver = None

    def __init__(self):
        # Load digit reader
        self.__digitReader = load_model("model/digitReader.h5")

        # Create GUI main window
        self.__mainWindow = tk.Tk()
        self.__mainWindow.title("Sudoku Solver CV")
        self.__mainWindow.geometry("%dx%d+%d+%d" % (540, 540, 50, 50))
        self.__mainWindow.resizable(False, False)
        self.__mainWindow.bind('<Escape>', lambda m: self.__killMainWin())
        self.__mainWindow.protocol("WM_DELETE_WINDOW", self.__killMainWin)

        # Create Grid
        self.__grid = tk.Frame(self.__mainWindow)
        self.__grid["highlightbackground"] = "black"
        self.__grid["highlightthickness"] = 1
        self.__grid.place(relx=0.5, rely=0.4, anchor=tk.CENTER, width=362, height=362)

        self.__cells = np.empty((9, 9)).astype(tk.Entry)
        self.__intVars = np.empty((9, 9)).astype(tk.IntVar)

        for i in range(0, 360, 40):
            for j in range(0, 360, 40):
                var = tk.IntVar()
                var.set("")
                cell = tk.Entry(self.__grid)
                cell["font"] = "Helvetica 24 bold"
                cell['bg'] = "white"
                cell["justify"] = tk.CENTER
                cell["highlightbackground"] = "black"
                cell["highlightthickness"] = 1
                cell["textvariable"] = var
                cell.place(width=40, height=40, x=j, y=i)
                self.__cells[i // 40, j // 40] = cell
                self.__intVars[i // 40, j // 40] = var

        # Webcam Enable Button
        self.__webcamButton = tk.Button(self.__mainWindow, command=self.__enableWebcam)
        self.__webcamButton["text"] = "Launch Webcam"
        self.__webcamButton["font"] = "Helvetica 12 bold"
        self.__webcamButton.place(width=154, height=36, relx=0.35, rely=0.80, anchor=tk.CENTER)

        # Upload Image Button
        self.__uploadButton = tk.Button(self.__mainWindow, command=self.__uploadImage)
        self.__uploadButton["text"] = "Upload Image"
        self.__uploadButton["font"] = "Helvetica 12 bold"
        self.__uploadButton.place(width=154, height=36, relx=0.65, rely=0.80, anchor=tk.CENTER)

        # Clear Button
        self.__clearButton = tk.Button(self.__mainWindow, command=self.__clearGrid)
        self.__clearButton["text"] = "Clear Grid"
        self.__clearButton["font"] = "Helvetica 12 bold"
        self.__clearButton.place(width=154, height=36, relx=0.5, rely=0.90, anchor=tk.CENTER)

        # Tutorial Button
        self.__tutorialButton = tk.Button(self.__mainWindow, command=self.__showInfo)
        self.__tutorialButton["text"] = "i"
        self.__tutorialButton["font"] = "Courier 12 bold"
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

        self.__subtitles[0] = "1. Click on 'Launch Webcam' to open the webcam for\nreading an unsolved Sudoku puzzle."
        self.__subtitles[1] = "2. Hold up the Sudoku puzzle in front of the webcam."
        self.__subtitles[2] = "3. Move the Sudoku puzzle closer when prompted to."
        self.__subtitles[3] = "4. Move the Sudoku puzzle further when prompted to."
        self.__subtitles[4] = "5. Stop moving tbe puzzle when prompted to."
        self.__subtitles[5] = "6. The white cells make up the current state, \nthe green cells make up the solution."

        self.__tutorialTextVar = tk.StringVar()

        # Launch the Tkinter GUI
        self.__mainWindow.mainloop()

    def __updateGrid(self, sudokuGrid, newCoordinates):
        for i in range(9):
            for j in range(9):
                self.__intVars[i, j].set(sudokuGrid[i, j])
                self.__cells[i, j]["bg"] = "green" if (i, j) in newCoordinates else "white"
                self.__cells[i, j]["font"] = "Helvetica 16 bold" if (i, j) in newCoordinates else "Helvetica 16"

    def __clearGrid(self):
        for i in range(9):
            for j in range(9):
                self.__intVars[i, j].set("")
                self.__cells[i, j]['bg'] = "white"

    def __killMainWin(self):
        self.__mainWindow.destroy()
        self.__mainWindow.quit()

    def __killWebcamWin(self):
        self.__webcamButton["state"] = "normal"
        self.__webcamWin.destroy()
        self.__webcamWin.quit()
        self.__vc.release()

    def __killTutorialWin(self):
        self.__tutorialButton["state"] = "active"
        self.__tutorialWindow.destroy()
        self.__tutorialWindow.quit()

    def __enableWebcam(self):
        # Create the webcam
        self.__vc = cv2.VideoCapture(0)
        self.__vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        self.__vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        success, img = self.__vc.read()
        if success:
            # Disable webcam button
            self.__webcamButton["state"] = "disable"

            # Create a child window that will contain the webcam video
            x, y = self.__mainWindow.winfo_x(), self.__mainWindow.winfo_y()
            self.__webcamWin = tk.Toplevel(self.__mainWindow)
            self.__webcamWin.geometry("1020x760+%d+%d" % (x + 600, y))
            self.__webcamWin.resizable(False, False)
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
                    self.__updateGrid(sudokuPuzzle, blankSquares)

        # Display next image onto webcam window
        cv2Img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        webcamImg = Image.fromarray(cv2Img)
        imgtk = ImageTk.PhotoImage(image=webcamImg)
        self.__webcamLabel.imgtk = imgtk
        self.__webcamLabel.configure(image=imgtk)
        self.__webcamLabel.after(10, self.__showFrame)

    def __uploadImage(self):
        # if not image file, show error message
        filePath = filedialog.askopenfilename()
        if not filePath:
            return None

        if not filePath.endswith((".png", ".jpg", "jpeg")):
            self.__showFileExtensionError()
            return None

        # read and preprocess the image
        img = cv2.imread(filePath)
        if img is None:
            self.__showIllegalConstraintsError(2)
            return None

        self.__puzzleFinder = PuzzleFinder(img, self.__digitReader)
        self.__sudokuSolver = SudokuSolver()

        # if numpy array is valid and can be solved, update the grid
        hasGrid = self.__puzzleFinder.getGridCornersUpload()

        # If contour is found, extract the puzzle from the image and solve the puzzle
        if hasGrid:
            # Extract puzzle and solve it
            flag = self.__puzzleFinder.extractGridFromCorners()
            if not flag:
                self.__showIllegalConstraintsError(4)
                return None

            sudokuPuzzle, blankSquares = self.__puzzleFinder.analyzeSquares()

            # Solve the puzzle only if all constraints are met
            if self.__sudokuSolver.isValidPuzzle(sudokuPuzzle):
                self.__sudokuSolver.setGrid(sudokuPuzzle)
                if self.__sudokuSolver.solveSudoku():
                    self.__updateGrid(sudokuPuzzle, blankSquares)
            else:
                self.__showIllegalConstraintsError(5)
        else:
            self.__showIllegalConstraintsError(3)

    def __showInfo(self):
        self.__tutorialButton["state"] = "disable"
        # Create a child window that will contain the tutorial
        x, y = self.__mainWindow.winfo_x(), self.__mainWindow.winfo_y()
        self.__tutorialWindow = tk.Toplevel(self.__mainWindow)
        self.__tutorialWindow.title("Sudoku Solver CV Tutorial")
        self.__tutorialWindow.geometry("1020x840+%d+%d" % (x + 600, y))
        self.__tutorialWindow.resizable(False, False)
        self.__tutorialWindow.bind('<Escape>', lambda w: self.__killTutorialWin())
        self.__tutorialWindow.protocol("WM_DELETE_WINDOW", self.__killTutorialWin)

        # Assign first image and subtitle to tutorial window
        self.__tutorialImage = tk.Label(self.__tutorialWindow)
        self.__tutorialImage.pack(side="top")
        self.__tutorialSubtitle = tk.Label(self.__tutorialWindow, textvariable=self.__tutorialTextVar, height=2)
        self.__tutorialSubtitle.place(relx=0.325, rely=0.925)
        self.__pageIndex = 0
        self.__updatePage(self.__pageIndex)

        # Back and Next button
        self.__backButton = tk.Button(self.__tutorialWindow, command=self.__backPage)
        self.__backButton["text"] = "Back"
        self.__backButton["font"] = "Helvetica 12 bold"
        self.__backButton["state"] = "disable"
        self.__backButton.place(width=60, relx=0.025, rely=0.925)
        self.__nextButton = tk.Button(self.__tutorialWindow, command=self.__nextPage)
        self.__nextButton["text"] = "Next"
        self.__nextButton["font"] = "Helvetica 12 bold"
        self.__nextButton.place(width=60, relx=0.925, rely=0.925)

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
            self.__backButton["state"] = "active"
        self.__pageIndex += 1
        self.__updatePage(self.__pageIndex)
        if self.__pageIndex == self.__numPages-1:
            self.__nextButton["state"] = "disable"

    def __backPage(self):
        if self.__pageIndex == self.__numPages-1:
            self.__nextButton["state"] = "active"
        self.__pageIndex -= 1
        self.__updatePage(self.__pageIndex)
        if self.__pageIndex == 0:
            self.__backButton["state"] = "disable"

    @staticmethod
    def __showWebcamError():
        messagebox.showerror("Error", "Webcam did not open successfully. ERROR 000")

    @staticmethod
    def __showIllegalConstraintsError(err):
        messagebox.showerror("Error",
                             "Either the puzzle entered does not meet all sudoku constraints or the puzzle "
                             "was not read correctly. \nERROR %03d" % err)

    @staticmethod
    def __showFileExtensionError():
        messagebox.showerror("Error", "File must have a .png, .jpg, or .jpeg extension. ERROR 001")
