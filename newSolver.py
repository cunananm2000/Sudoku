import math
import time
from enum import Enum
from testData import *

class Status(Enum):
    SOLVED = 0
    IN_PROGRESS = 1
    IMPOSSIBLE = 2

class Grid(object):
    def __init__(self, size, secW, secH, depth=0):
        if (size % secW + size % secH) != 0:
            return
        
        self._size = size
        self._secW = secW # Width of each section
        self._secH = secH # Height of each section
        self._nSecsW = math.floor(size/self._secW) # Number of sections along width
        self._nSecsH = math.floor(size/self._secH) # Number of sections along height
        self._status = Status.IN_PROGRESS
        self._solved = []
        self._possible = []
        self._nSolved = 0
        self._queue = []
        self._depth = depth

        for i in range(size):
            solvedRow = []
            posRow = []
            for j in range(size):
                solvedRow.append(False)
                posRow.append(self.allNumbers())
            self._solved.append(solvedRow)
            self._possible.append(posRow)

    def load(self,sampleGrid):
        if len(sampleGrid) != self._size:
            return False
        for row in sampleGrid:
            if len(row) != self._size:
                return False
        
        # nSolved = 0
        for i in range(self._size):
            for j in range(self._size):
                n = sampleGrid[i][j]
                if (n != 0):
                    self.addToQueue(n,i,j)

    def allNumbers(self):
        numbers = []
        for i in range(self._size):
            numbers.append(1+i)
        return numbers

    def printOut(self,showPossible=False):
        display = []
        for i in range(0,self._size):
            tempRow = []
            for j in range(0,self._size):
                # print(self._solved[i][j])
                if (self._solved[i][j]):
                    tempRow += [self._possible[i][j][0]]
                else:
                    tempRow += ["?"]
            display += [tempRow]

        for i in range(0, self._size):
            tempRow = ""
            for j in range(0,self._size-1):
                tempRow += str(display[i][j]) + " "
                if ((j + 1) % self._secW) == 0:
                    tempRow += "# "
            tempRow += str(display[i][self._size-1])
            print(tempRow)

            if ((i + 1) % self._secH) == 0 and i != self._size - 1:
                tempRow = "# "*(self._size + round(self._size/self._secW)-2) + "#"
                print(tempRow)

        if (showPossible):
            for i in range(self._size):
                for j in range(self._size):
                    if (not self._solved[i][j]):
                        print(i,j,self._possible[i][j])

    def writeIn(self,n,x,y):
        # print("Writing in",x,y,"at",n)
        # if (self._status != Status.IN_PROGRESS):
        #     print("Dying here")
        #     return False

        if (self._solved[x][y]):
            if (self._possible[x][y][0] != n):
                self._status = Status.IMPOSSIBLE
                self._nSolved = 0
                return False
            else:
                return True

        self._solved[x][y] = True
        self._possible[x][y] = [n]
        self._nSolved += 1

        # print(self._depth*"-",x,y,":",n)

        if self._nSolved == self._size**2:
            self._status = Status.SOLVED
            return True

        for j in range(self._size):
            if (j == y):
                continue
            if (n in self._possible[x][j]):
                self._possible[x][j].remove(n)
                if (len(self._possible[x][j]) == 0):
                    self._status = Status.IMPOSSIBLE
                    self._nSolved = 0
                    # print("Reached an impossible place")
                    return False
                elif (len(self._possible[x][j]) == 1 and not self._solved[x][j]):
                    self.addToQueue(self._possible[x][j][0],x,j)

        for i in range(self._size):
            if (i == x):
                continue
            if (n in self._possible[i][y]):
                self._possible[i][y].remove(n)
                if (len(self._possible[i][y]) == 0):
                    self._status = Status.IMPOSSIBLE
                    self._nSolved = 0
                    # print("Reached an impossible place")
                    return False
                elif (len(self._possible[i][y]) == 1 and not self._solved[i][y]):
                    self.addToQueue(self._possible[i][y][0],i,y)
        
        tl = self.getTLofSec(x,y)
        for i in range(self._secH):
            for j in range(self._secW):
                if (tl[0]+i == x and tl[1]+j == y):
                    continue
                if (n in self._possible[tl[0]+i][tl[1]+j]):
                    self._possible[tl[0]+i][tl[1]+j].remove(n)
                    if (len(self._possible[tl[0]+i][tl[1]+j]) == 0):
                        self._status = Status.IMPOSSIBLE
                        # print("Reached an impossible place")
                        return False
                    elif (len(self._possible[tl[0]+i][tl[1]+j]) == 1 and not self._solved[tl[0]+i][tl[1]+j]):
                        self.addToQueue(self._possible[tl[0]+i][tl[1]+j][0],tl[0]+i,tl[1]+j)
                
        return True

    def getTLofSec(self,x,y):
        tl = [0,0]
        tl[0] = self._secH*math.floor(x/self._secH)
        tl[1] = self._secW*math.floor(y/self._secW)
        return tl

    def addToQueue(self,n,x,y):
        self._queue.append([n,x,y])

    def solveByElimination(self):
        if (self._status != Status.IN_PROGRESS):
            return False
        # Clear each row
        # Clear each column
        # Clear each block
        currentSolved = self._nSolved
        for i in range(self._size):
            row = []
            for j in range(self._size):
                row.append([i,j])
            self.solveGroup(row)

        for j in range(self._size):
            col = []
            for i in range(self._size):
                row.append([i,j])
            self.solveGroup(col)

        for x in range(self._nSecsH):
            for y in range(self._nSecsW):
                tlX = self._secH*x
                tlY = self._secW*y
                sec = []
                for i in range(self._secH):
                    for j in range(self._secW):
                        sec.append([tlX+i,tlY+j])
                self.solveGroup(sec)

        return (self._nSolved > currentSolved)

    
    def solveGroup(self,group):
        numbers = self.allNumbers()
        emptys = []
        # Find out what numbers aren't accounted for
        # Find out what available spaces there are
        for pos in group:
            if (self._solved[pos[0]][pos[1]]):
                # print(pos[0],pos[1],self._possible[pos[0]][pos[1]])
                try:
                    numbers.remove(self._possible[pos[0]][pos[1]][0])
                except:
                    self._status = Status.IMPOSSIBLE
                    # print("Reached an impossible state")
                    return
            else:
                emptys.append(pos)
        
        for n in numbers:
            chosen = None
            found = False
            for pos in emptys:
                # May be solved in the process
                if self._solved[pos[0]][pos[1]]:
                    continue
                if n in self._possible[pos[0]][pos[1]]:
                    if found:
                        found = False
                        break
                    else:
                        chosen = pos
                        found = True
            if found:
                self.writeIn(n,chosen[0],chosen[1])
                self.doQueue()
        
    def doQueue(self):
        currentSolved = self._nSolved
        while (len(self._queue) != 0):
            self.writeIn(self._queue[0][0],self._queue[0][1],self._queue[0][2])
            self._queue = self._queue[1:]
        return (self._nSolved > currentSolved)

    def clone(self):
        newGrid = Grid(self._size,self._secW,self._secH,self._depth+1)
        for i in range(0,self._size):
            for j in range(0,self._size):
                if (self._solved[i][j]):
                    newGrid.writeIn(self._possible[i][j][0],i,j)
        # print("Clone:")
        # newGrid.printOut()
        return newGrid

    def getNatXY(self,x,y):
        if (self._solved[x][y]):
            assert len(self._possible[x][y]) == 1
            return self._possible[x][y][0]
        else:
            return 0

    def getStatus(self):
        return self._status

    def adapt(self,otherGrid):
        for i in range(0,self._size):
            for j in range(0,self._size):
                self.writeIn(otherGrid.getNatXY(i,j),i,j)
        self._status = otherGrid.getStatus()
        # for i in range(0,self._size):
        #     for j in range(0,self._size):
        #         print(self.getNatXY(i,j))

    def solveByGuess(self):
        if (self._status != Status.IN_PROGRESS):
            return False

        changed = False
        for i in range(0,self._size):
            for j in range(0,self._size):
                if (not self._solved[i][j] and len(self._possible[i][j]) <= 4):
                    works = -1
                    nWorks = 0
                    k = 0
                    while (k < len(self._possible[i][j])):
                        # print(k,len(self._possible[i][j]))
                        tempGrid = self.clone()
                        tempGrid.writeIn(self._possible[i][j][k],i,j)
                        # print("depth:",self._depth,'  '*self._depth,"Guessing",self._possible[i][j][k],"at",i,j)
                        tempGrid.solve()
                        if (tempGrid.getStatus() == Status.SOLVED):
                            # print("Hey this one worked")
                            nWorks = 1
                            self.adapt(tempGrid)
                            return True
                        # elif (tempGrid.getStatus() == Status.IN_PROGRESS):
                        if (tempGrid.getStatus() != Status.IMPOSSIBLE):
                            nWorks += 1
                            works = self._possible[i][j][k]
                            if (nWorks >= 2):
                                break
                        k += 1
                    if (nWorks == 1):
                        # print("Found that",works,"Works")
                        changed = True
                        self.writeIn(works,i,j)
                        # print("Depth:",self._depth,'  '*self._depth,"GOOD:",works,"at",i,j)
                        progress = True
                        while progress:
                            progress = (self.doQueue() or self.solveByElimination())
        return changed

    def solve(self):
        progress = True
        while progress:
            # print("going")
            progress = (self.doQueue() or self.solveByElimination())
        if (self._status == Status.IN_PROGRESS):
            print("Done all logical steps, moving onto guessing")
            if (self._depth < 2):
                self.solveByGuess()

    def getGrid(self):
        ret = []
        for i in range(self._size):
            row = []
            for j in range(self._size):
                if self._solved[i][j]:
                    row.append(self._possible[i][j][0])
                else:
                    row.append(0)

            ret.append(row)
        return ret
        

if __name__ == "__main__":
    mainGrid = Grid(9,3,3)
    # mainGrid.writeIn(1,5,5)
    # nSolved = 0
    # for i in range(9):
    #     for j in range(9):
    #         n = exp2Numbers[i][j]
    #         if (n != 0):
    #             mainGrid.addToQueue(n,i,j)
    #             nSolved += 1
    mainGrid.load(evilNumbers)
    start = time.process_time()
    mainGrid.solve()
    print("TIME:",time.process_time() - start, mainGrid.getStatus())
    mainGrid.printOut()
    grid = mainGrid.getGrid()
    print(grid)
    # print("nSolved:",nSolved,'->',mainGrid._nSolved)