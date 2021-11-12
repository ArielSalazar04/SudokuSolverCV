import numpy as np
import tkinter as tk


class App:
    __mainWindow = None
    __webcamWindow = None
    __webcamLabel = None
    __webcamButton = None
    __grid = None
    __clearButton = None
    __infoButton = None

    __digitReader = None
    __cells = np.empty((9, 9)).astype(tk.Entry)
    __intVars = np.empty((9, 9)).astype(tk.IntVar)

    def __init__(self):
        # Create GUI main window
        self.__mainWindow = tk.Tk()
        self.__mainWindow.title("Sudoku Solver CV")
        self.__mainWindow.geometry("%dx%d+%d+%d" % (540, 540, 50, 50))
        self.__mainWindow.resizable(False, False)
        self.__mainWindow.bind('<Escape>', lambda: self.__mainWindow.quit())

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

    def __enableWebcam(self):
        pass

    def __showFrame(self):
        pass

    def __showInfo(self):
        pass

