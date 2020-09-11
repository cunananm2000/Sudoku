import time
from newSolver import Grid, Status
from sudokuSplitter import extractGrid
import sys
import cv2
from testData import *

def main():
    mainGrid = Grid(9,3,3)

    start = time.process_time()
    img = cv2.imread(sys.argv[1])

    sampleGrid = extractGrid(img)
    if sampleGrid is None:
        return


    mainGrid.load(sampleGrid)

    mainGrid.solve()
    print("TIME:",time.process_time() - start, mainGrid.getStatus())
    mainGrid.printOut()
    grid = mainGrid.getGrid()
    # print("nSolved:",nSolved,'->',mainGrid._nSolved)

if __name__ == "__main__":
    main()