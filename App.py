import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from PuzzleFinder import PuzzleFinder


class App:
    __mainWindow = None
    __webcamWindow = None
    __webcamLabel = None
    __webcamButton = None
    __grid = None
    __clearButton = None
    __infoButton = None
    __vc = None
    __puzzleFinder = None

    __digitReader = None
    __cells = np.empty((9, 9)).astype(tk.Entry)
    __intVars = np.empty((9, 9)).astype(tk.IntVar)

    def __init__(self):
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

        for i in range(0, 360, 40):
            for j in range(0, 360, 40):
                var = tk.IntVar()
                var.set("")
                cell = tk.Entry(self.__grid)
                cell["font"] = "Helvetica 24 bold"
                cell["justify"] = tk.CENTER
                cell["state"] = "disabled"
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
        self.__webcamButton.place(width=154, height=36, relx=0.5, rely=0.80, anchor=tk.CENTER)

        # Clear Button
        self.__clearButton = tk.Button(self.__mainWindow, command=self.__clearGrid)
        self.__clearButton["text"] = "Clear Grid"
        self.__clearButton["font"] = "Helvetica 12 bold"
        self.__clearButton.place(width=154, height=36, relx=0.5, rely=0.90, anchor=tk.CENTER)

        # Information Button
        self.__infoButton = tk.Button(self.__mainWindow, command=self.__showInfo)
        self.__infoButton.place(width=36, height=36, relx=0.9, rely=0.90, anchor=tk.CENTER)

        # Launch the Tkinter GUI
        self.__mainWindow.mainloop()

    def __updateGrid(self):
        pass

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

            self.__puzzleFinder = PuzzleFinder(img)
            self.__showFrame()
            self.__webcamWin.mainloop()

        else:
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
        hasGrid = self.__puzzleFinder.getGridContour()

        # If contour is found, extract the puzzle from the image and solve the puzzle
        if hasGrid:
            # Extract puzzle and solve it
            self.__puzzleFinder.extractGridFromContour()
            sudokuPuzzle, blankSquares = self.__puzzleFinder.analyzeSquares()

            # Solve the puzzle only if all constraints are met

        # Display next image onto webcam window
        cv2Img = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGBA)
        webcamImg = Image.fromarray(cv2Img)
        imgtk = ImageTk.PhotoImage(image=webcamImg)
        self.__webcamLabel.imgtk = imgtk
        self.__webcamLabel.configure(image=imgtk)
        self.__webcamLabel.after(10, self.__showFrame)

    @staticmethod
    def __showInfo(self):
        pass

    @staticmethod
    def __showWebcamError():
        messagebox.showerror("Error", "Webcam did not open successfully.")
