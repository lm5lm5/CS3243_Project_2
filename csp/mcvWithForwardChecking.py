import sys
import copy
import time
from heapq import heappop, heappush, heapify

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    def solve(self):
        nine = 9
        visitedRows = [[False for j in range(10)] for i in range(9)]
        visitedCols = [[False for j in range(10)] for i in range(9)]
        visitedBlocks = [[[False for k in range(10)] for i in range(3)] for j in range(3)]
        possibleValues = [[[False for k in range(10)] for i in range(9)] for j in range(9)]
        possibleValuesCounter = [[9 for j in range(9)] for i in range(9)]
        isSafe = lambda row, col, num: (not visitedRows[row][num]) and (not visitedCols[col][num])  and (not visitedBlocks[row // 3][col // 3][num])
        isUnfilledCell = lambda row, col: self.ans[row][col] == 0

        # Initialize possible values of each cell
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0: # IsEmpty block
                    for k in range(1, 10):
                        possibleValues[i][j][k] = True
        
        for i in range(9):
            for j in range(9):
                num = puzzle[i][j]
                if num != 0:
                    visitedRows[i][num] = True
                    visitedCols[j][num] = True
                    for k in range(9):
                        if possibleValues[i][k][num]:
                            possibleValues[i][k][num] = False
                            possibleValuesCounter[i][k] -= 1
                        if possibleValues[k][j][num]:
                            possibleValues[k][j][num] = False
                            possibleValuesCounter[k][j] -= 1

                    x = i // 3
                    y = j // 3
                    visitedBlocks[x][y][num] = True

                    x *= 3
                    y *= 3
                    for a in range(3):
                        for b in range(3):
                            s = x + a
                            t = y + b
                            if possibleValues[s][t][num]:
                                possibleValues[s][t][num] = False
                                possibleValuesCounter[s][t] -= 1

        setCells = []                           # stack of set cells
        unsetCells = [set() for j in range(10)] # set cells into lists according to the domain size of the cell
        hasUnfilledCells = False

        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    size = possibleValuesCounter[i][j]
                    unsetCells[size].add(i * nine + j)
                    hasUnfilledCells = True

        if not hasUnfilledCells:
            return self.ans

        def discardNumFromDomain(row, col, num): # Returns true if the discard did not lead an empty domain i.e. will fail later
            cell = row * nine + col
            prevLen = possibleValuesCounter[row][col]
            unsetCells[prevLen].discard(cell)
            possibleValues[row][col][num] = False
            possibleValuesCounter[row][col] -= 1
            newLen = possibleValuesCounter[row][col]
            unsetCells[newLen].add(cell)
            return newLen > 0
            

        def addBackNumToDomain(row, col, num):
            cell = row * nine + col
            prevLen = possibleValuesCounter[row][col]
            unsetCells[prevLen].discard(cell)
            possibleValues[row][col][num] = True
            possibleValuesCounter[row][col] += 1
            newLen = possibleValuesCounter[row][col]
            unsetCells[newLen].add(cell)

        self.biggestDomain = 0
        def getNextUnsetCell():
            for i in range(len(unsetCells)):
                if len(unsetCells[i]) > 0:
                    if i > self.biggestDomain:
                        self.biggestDomain = i
                    return unsetCells[i].pop()

        currElement = getNextUnsetCell()
        currR = currElement // nine
        currC = currElement % nine
        currVal = 1

        backtracks = 0
        # Main backtracking loop
        while True:
            while currVal <= 9 and not possibleValues[currR][currC][currVal]:
                currVal += 1

            if currVal <= 9:
                self.ans[currR][currC] = currVal
                visitedRows[currR][currVal] = True
                visitedCols[currC][currVal] = True
                blockR = currR // 3
                blockC = currC // 3
                visitedBlocks[blockR][blockC][currVal] = True

                isPossibleValue = True

                # Forward checking
                for i in range(9):
                    if isUnfilledCell(currR, i) and possibleValues[currR][i][currVal] and not discardNumFromDomain(currR, i, currVal):
                        isPossibleValue = False
                        break
                    if isUnfilledCell(i, currC) and possibleValues[i][currC][currVal] and not discardNumFromDomain(i, currC, currVal):
                        isPossibleValue = False
                        break

                if isPossibleValue:
                    blockR *= 3
                    blockC *= 3
                    for i in range(3):
                        for j in range(3):
                            a = blockR + i
                            b = blockC + j
                            if isUnfilledCell(a, b) and possibleValues[a][b][currVal] and not discardNumFromDomain(a, b, currVal):
                                isPossibleValue = False
                                break
                        if not isPossibleValue:
                                break

                setCells.append((currR, currC, currVal))

                nextUnsetCell = getNextUnsetCell()

                if nextUnsetCell == None:
                    print("backtracks ", backtracks)
                    print("biggestDomain ", self.biggestDomain)
                    return self.ans

                currR = nextUnsetCell // nine
                currC = nextUnsetCell % nine
                currVal =  1 if isPossibleValue else 10

            elif len(setCells) > 0: # Backtrack if no more available numbers
                backtracks += 1
                self.ans[currR][currC] = 0 # reset to unfilled cell
                currR, currC, currVal = setCells.pop()
                visitedRows[currR][currVal] = False
                visitedCols[currC][currVal] = False
                blockR = currR // 3
                blockC = currC // 3
                visitedBlocks[blockR][blockC][currVal] = False

                # Reverse the forward checking
                for i in range(9):
                    if isUnfilledCell(currR, i) and not possibleValues[currR][i][currVal] and isSafe(currR, i, currVal):
                        addBackNumToDomain(currR, i, currVal)
                    if isUnfilledCell(i, currC) and not possibleValues[i][currC][currVal] and isSafe(i, currC, currVal):
                        addBackNumToDomain(i, currC, currVal)

                blockR *= 3
                blockC *= 3
                for i in range(3):
                    for j in range(3):
                        a = blockR + i
                        b = blockC + j
                        if isUnfilledCell(a, b) and not possibleValues[a][b][currVal] and isSafe(a, b, currVal):
                            addBackNumToDomain(a, b, currVal)

                currVal += 1

        return None

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    start_time = time.time()

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    print("time elapsed in seconds: %s" % (time.time() - start_time))

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
