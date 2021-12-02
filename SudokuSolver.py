import numpy as np


class SudokuSolver:
    __grid = None

    def __init__(self, grid=None):
        self.__grid = grid

    def hasGrid(self):
        return self.__grid is not None

    def setGrid(self, grid):
        self.__grid = grid

    def solveSudoku(self):
        return self.__backtracking() if self.hasGrid() else None

    def __backtracking(self):
        if self.__isComplete():
            return True

        r, c = self.__findNextBlankCell()

        for i in range(1, 10):
            if self.__meetsConstraints(r, c, i):
                self.__grid[r, c] = i
                flag = self.__backtracking()
                if flag:
                    return True
                self.__grid[r, c] = 0

        return False

    def __isComplete(self):
        return 0 not in self.__grid

    def __findNextBlankCell(self):
        l1, l2 = np.where(self.__grid == 0)
        return l1[0], l2[0]

    def __meetsConstraints(self, r, c, num):
        if num in self.__grid[:, c] or num in self.__grid[r, :]:
            return False

        r = r // 3 * 3
        c = c // 3 * 3

        if num in self.__grid[r:r + 3, c:c + 3].flatten():
            return False

        return True

    @staticmethod
    def isValidPuzzle(grid):
        seen = set()
        # check all horizontal
        for r in range(9):
            for c in range(9):
                val = grid[r, c]
                if val != 0:
                    if val in seen:
                        return False
                    seen.add(val)
            seen.clear()

        # check all vertical
        for c in range(9):
            for r in range(9):
                val = grid[r, c]
                if val != 0:
                    if val in seen:
                        return False
                    seen.add(val)
            seen.clear()

        # check all 3x3 squares
        for c in range(0, 9, 3):
            for r in range(0, 9, 3):
                for j in range(c, c + 3):
                    for i in range(r, r + 3):
                        val = grid[i, j]
                        if val != 0:
                            if val in seen:
                                return False
                            seen.add(val)
                seen.clear()

        return True

    @staticmethod
    def getAllConflicts(grid):
        conflicts = set()
        lookupTable = dict()

        # row conflicts
        for row in range(9):
            for col in range(9):
                if not grid[row, col] == 0:
                    if grid[row, col] in lookupTable:
                        conflicts.add((row, col))
                        conflicts.add((lookupTable[grid[row, col]]))
                    else:
                        lookupTable[grid[row, col]] = (row, col)
            lookupTable.clear()

        # column conflicts
        for col in range(9):
            for row in range(9):
                if not grid[row, col] == 0:
                    if grid[row, col] in lookupTable:
                        conflicts.add((row, col))
                        conflicts.add((lookupTable[grid[row, col]]))
                    else:
                        lookupTable[grid[row, col]] = (row, col)
            lookupTable.clear()

        # 3x3 square conflicts
        for c in range(0, 9, 3):
            for r in range(0, 9, 3):
                for j in range(c, c + 3):
                    for i in range(r, r + 3):
                        if not grid[i, j] == 0:
                            if grid[i, j] in lookupTable:
                                conflicts.add((i, j))
                                conflicts.add((lookupTable[grid[i, j]]))
                            else:
                                lookupTable[grid[i, j]] = (i, j)
                    lookupTable.clear()

        return conflicts
