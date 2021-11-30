# SudokuSolverCV
A software system that solves Sudoku puzzles using Computer Vision (opencv-python), Deep Learning (tensorflow), 
and Iterative Backtracking Algorithm. 

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all required libraries.
```bash
pip install -r requirements.txt
```

## Usage
The following bash command can be used to start the software system:
```bash
python main.py
```
To close out of any windows, press the ``ESC`` key.

## Error Codes
| Code | Description |
| ---- | ----------- |
|  000 | Webcam did not open successfully. |
|  001 | Invalid image file extension. |
|  002 | Image file could not be read. |
|  003 | Grid was not found in image. |
|  004 | Detected puzzle has invalid constraints or was not read properly. |
