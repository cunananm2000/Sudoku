import math
from enum import Enum

class Status(Enum):
    SOLVED = 0
    IN_PROGRESS = 1
    IMPOSSIBLE = 2

class Grid(object):
    def __init__(self, size, secW, secH, layersDeep=0):
        if (size % secW + size % secH) != 0:
            return

        self._size = size
        self._secW = secW # Width of each section
        self._secH = secH # Height of each section
        self._nSecsW = math.floor(size/self._secW) # Number of sections along width
        self._nSecsH = math.floor(size/self._secH) # Number of sections along height
        self._positions = {}
        self._assigned = [] # 2D array of each squares are solved
        self._status = Status.IN_PROGRESS
        self._nSolved = 0
        self._layersDeep = layersDeep

        for i in range(1,size+1):
            self._positions[i] = []

        for i in range(0,size):
            tempRow = [-1]*size
            self._assigned += [tempRow]
        

    def parsePos(self,x,y):
        sX = math.floor(x/self._secH)
        sY = math.floor(y/self._secW)
        return [x,y,sX*math.floor(self._size/self._secW)+sY]

    def writeIn(self, n, x, y):
        if (self._status != Status.IN_PROGRESS):
            return False

        if (n > self._size or n <= 0):
            return False

        if (self._assigned[x][y] != -1):
            return False

        self._positions[n] += [self.parsePos(x,y)]
        self._assigned[x][y] = n
        self._nSolved += 1

        if self._nSolved == self._size**2:
            self._status = Status.SOLVED

        # if self._layersDeep == 0:
            # print("Writing in",n,"at",x,y)
        return True

    def printOut(self):
        display = []
        for i in range(0,self._size):
            tempRow = []
            for j in range(0,self._size):
                if (self._assigned[i][j] != -1):
                    tempRow += [self._assigned[i][j]]
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

    # For each square, see what's possible
    # If only one number possible, fill it with that
    # Keep going until no 'progress' is made with this method
    def solveBySquares(self):
        progress = True
        while progress and self._status == Status.IN_PROGRESS:
            progress = False
            for i in range(0,self._size):
                for j in range(0,self._size):
                    if (self._assigned[i][j] != -1):
                        continue

                    possible = self.getPossible(i,j)

                    if len(possible) == 0:
                        self._status = Status.IMPOSSIBLE
                        return False
                    elif len(possible) == 1:
                        self.writeIn(possible[0],i,j)
                        progress = True

    def allNumbers(self,index=1):
        temp = []
        for k in range(index,self._size+index):
            temp += [k]
        return temp

    def clone(self):
        tempGrid = Grid(self._size, self._secW, self._secH,self._layersDeep+1)
        for i in range(0,self._size):
            for j in range(0,self._size):
                if self._assigned[i][j] != -1:
                    tempGrid.writeIn(self._assigned[i][j],i,j)
        return tempGrid

    def copy(self, grid):
        for i in range(0,self._size):
            for j in range(0,self._size):
                self.writeIn(grid.getSquare(i,j),i,j)
        # assert self.equals(grid)

    def equals(self,grid):
        for i in range(0,self._size):
            for j in range(0,self._size):
                if self._assigned[i][j] != grid.getSquare(i,j):
                    return False
        return True

    def getStatus(self):
        return self._status

    def getSquare(self,x,y):
        return self._assigned[x][y]

    def solveByGuess(self):
        if self._status != Status.IN_PROGRESS:
            return False

        for i in range(0,self._size):
            for j in range(0,self._size):
                if self._assigned[i][j] != -1:
                    continue
                possible = self.getPossible(i,j)
                if len(possible) == 0:
                    self._status = Status.IMPOSSIBLE
                    return False
                elif len(possible) == 1:
                    self.writeIn(possible[0],i,j)
                    self.solveByNumbers()
                elif len(possible) <= 4:
                    # print("Gonna guess from",possible,"at",i,j)
                    candidate = -1
                    found = False
                    for considered in possible:
                        tempGrid = self.clone()
                        tempGrid.writeIn(considered,i,j)
                        tempGrid.solve()
                        if tempGrid.getStatus() == Status.IMPOSSIBLE:
                            continue
                        elif tempGrid.getStatus() == Status.SOLVED:
                            self.copy(tempGrid)
                            self._status = Status.SOLVED
                            return True
                        else:
                            if candidate != -1:
                                candidate = considered
                                found = True
                            else:
                                found = False
                                break
                    
                    if found:
                        tempGrid.writeIn(candidate,i,j)

    def solve(self):
        self.solveByNumbers()
        self.solveBySquares()
        if self._layersDeep < 2:
            self.solveByGuess()

    def getPossible(self,x,y):
        # Find out which numbers are possible in a given square
        possible = self.allNumbers()
        
        # Clean up the row first
        for j in range(0,self._size):
            considered = self._assigned[x][j]
            if considered in possible:
                possible.remove(considered)

        for i in range(0,self._size):
            considered = self._assigned[i][y]
            if considered in possible:
                possible.remove(considered)

        sX = self._secH*math.floor(x/self._secH)
        sY = self._secW*math.floor(y/self._secW)
        for i in range(sX,sX+self._secH):
            for j in range(sY,sY+self._secW):
                considered = self._assigned[i][j]
                if considered in possible:
                    possible.remove(considered)

        # print(possible)
        return(possible)
    
    def getTLofSec(self,sec):
        sX = math.floor(sec/self._nSecsW)
        sY = sec % self._nSecsW
        return(sX*self._secH,sY*self._secW)

    # For each number 1..n
    #   Locate each one currently on the grid
    #   For each section without that number in it
    #       Find out which squares in that section can fit it
    def solveByNumbers(self):
        progress = True
        # nTries = 0
        while progress and self._status == Status.IN_PROGRESS:
            # print('*********',"TRY",nTries,'*********')
            progress = False
            for n in range(1,self._size+1):
                miniProgress = True
                # miniTry = 0
                while miniProgress and self._status == Status.IN_PROGRESS:
                    # print('---------',"miniTRY",miniTry,'---------')
                    possibleSections = self.allNumbers(0)
                    # print(possibleSections)
                    for pos in self._positions[n]:
                        if pos[2] in possibleSections:
                            possibleSections.remove(pos[2])
                    # print("Free for",n,':',possibleSections)
                    
                    miniProgress = False
                    for sec in possibleSections:
                        tl = self.getTLofSec(sec)
                        considered = []
                        for i in range(tl[0],tl[0]+self._secH):
                            for j in range(tl[1],tl[1]+self._secW):
                                if (self._assigned[i][j] == -1):
                                    considered += [[i,j]]
                        
                        i = 0
                        while i < len(considered):
                            earlyBreak = False
                            for pos in self._positions[n]:
                                # print("Comparing",considered[i],'to',pos)
                                if considered[i][0] == pos[0] or considered[i][1] == pos[1]:
                                    # print("     removing",considered[i])
                                    considered.remove(considered[i])
                                    earlyBreak = True
                                    break
                            # print("Remaining:",considered)
                            if not earlyBreak:
                                i += 1
                        
                        if len(considered) == 0:
                            self._status = Status.IMPOSSIBLE
                            # print("Early return")
                            return False
                        elif len(considered) == 1:
                            self.writeIn(n, considered[0][0], considered[0][1])
                            # print("Writing in",n,"at",considered[0][0]+1, considered[0][1]+1)
                            progress = True
                            miniProgress = True