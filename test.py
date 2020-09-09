from solver import Status,Grid
from testData import *
import time

if __name__ == "__main__":
    mainGrid = Grid(9,3,3)
    for i in range(9):
        for j in range(9):
            mainGrid.writeIn(diab3Numbers[i][j],i,j)
    
    mainGrid.printOut()

    print("-------------")

    start = time.process_time()
    mainGrid.solve()
    print("TIME:",time.process_time() - start)
    mainGrid.printOut()

    if mainGrid.getStatus() == Status.SOLVED:
        print("Solved")
    elif mainGrid.getStatus() == Status.IMPOSSIBLE:
        print("This is impossible")
    else:
        print("Timed out,",mainGrid._nSolved)