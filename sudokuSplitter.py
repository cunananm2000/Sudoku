import cv2
import numpy as np
import math
import sys
import pytesseract


cellSize = 56
border = 3

def cleanUp(img):
    rx = 500.0/img.shape[0]
    ry = 500.0/img.shape[1]
    r = max([rx,ry])


    img = cv2.resize(img,(0,0),fx=r,fy=r)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.addWeighted(img, 1.5, np.zeros(img.shape, img.dtype), 0, 0)

    img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,25,25)
    
    edged = cv2.Canny(img,60,180)
    
    im2, contours, hierarchy = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("No contours found")
        return None

    cnt = None
    maxArea = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > maxArea:
            maxArea = area
            cnt = c

    
    if cnt is None:
        print("No biggest contour")
        return None

    epsilon = 0.01*cv2.arcLength(cnt,True)
    approx = cv2.approxPolyDP(cnt,epsilon,True)


    if (approx.size != 8):
        print("Wrong shape of grid")
        return
    approx = approx.reshape(4,2)
    approx = np.array(approx.tolist(),np.float32)

    gridSize = cellSize*9
    final = np.array([
		[0, 0],
		[0, gridSize],
		[gridSize, gridSize],
		[gridSize, 0]], dtype = "float32")

    M = cv2.getPerspectiveTransform(approx, final)
    fixed = cv2.warpPerspective(img, M, (gridSize, gridSize))

    return fixed

def splitUp(grid):
    cells = []
    for i in range(0,9):
        row = []
        for j in range(0,9):
            cropped = grid[cellSize*i+border:cellSize*(i+1)-border, cellSize*j+border:cellSize*(j+1)-border]
            row.append(cropped)
        cells.append(row)
    return cells

def saveCells(cells):
    for i in range(len(cells)):
        for j in range(len(cells[i])):
            if cells[i][j] is not None:
                cv2.imwrite("digits/grid_"+str(i)+str(j)+".png",cells[i][j])

def removeBlackBorder(img,tol=0):
    mask = img>tol
    return img[np.ix_(mask.any(1),mask.any(0))]

def highlightDigit(cell):
    if cell is None:
        return None

    img = cv2.cvtColor(cell,cv2.COLOR_GRAY2RGB)
    # gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(cell,None,50,5,5)
    gray = cv2.bitwise_not(gray)
    gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]

    # cv2.imshow("gray",gray)
    # cv2.waitKey(0)

    edges = cv2.Canny(gray,1,1)

    output = cv2.connectedComponentsWithStats(gray, 8, cv2.CV_32S)
    labels = output[1]
    stats = output[2]
    sizes = stats[1:, -1]
    if len(output[2]) <= 1:
        # print("Huh")
        return None
    
    largest_label = 1 + np.argmax(output[2][1:, -1])
    # print(output[2])

    width,height = gray.shape[:2]


    x,y,w,h,_ = stats[largest_label]
    bX = x + w/2.0
    bY = y + h/2.0

    cX = width/2.0
    cY = height/2.0

    tX = cX - bX
    tY = cY - bY

    if (abs(tX) + abs(tY) > 15) or (w*h > 0.9 * width * height):
        # print("No central blob")
        return None

    img[labels != largest_label] = [255,255,255]

    img = img[y:y+h,x:x+w]
    return img

def highlightCells(cells):
    for i in range(len(cells)):
        for j in range(len(cells[i])):
            # print("Trying",i,j)
            cells[i][j] =  highlightDigit(cells[i][j])
            # print(cells[i][j] is not None)
            # if newCell is not None:
            #     cells[i][j] = newCell
    return cells

def thresh(x):
    if x < 2:
        return 0
    if x < 5:
        return 0
    return 1

def printLocations(cells):
    for i in range(len(cells)):
        row = []
        for j in range(len(cells)):
            if cells[i][j] is not None:
                row.append("X")
            else:
                row.append("-")
        print(" ".join(row))

def printCells(cells):
    for i in range(len(cells)):
        row = []
        # print(len(cells[i]))
        for j in range(len(cells[i])):
            if cells[i][j] != 0:
                row.append(str(cells[i][j]))
            else:
                row.append("?")
        # print(len(row))
        print(" ".join(row))

def addPadding(img,border=10):
    return cv2.copyMakeBorder(img,10,10,2,2,cv2.BORDER_CONSTANT,value=[255,255,255])

def hconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = min(im.shape[0] for im in im_list)
    im_list = [addPadding(im) for im in im_list]
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
                      for im in im_list]
    return cv2.hconcat(im_list_resize)
    

def flatten(a):
    temp = []
    for row in a:
        temp = temp + row
    return temp

def assertShape(grid,rows=9,cols=9):
    assert(grid is not None)
    assert(len(grid) == rows)
    for row in grid:
        assert(len(row) == cols)
    print("Passed shape test")

def getDigits(cells):
    line = flatten(cells)
    cellsWithDigits = list(filter(lambda x: x is not None, line))
    line = hconcat_resize_min(cellsWithDigits)
    # cv2.imshow("first",line)
    # cv2.waitKey(0)
    # cv2.imwrite("first.png",line)

    custom_config = r'--psm 6 outputbase digits'
    text = pytesseract.image_to_string(line, config=custom_config)

    # print(text)

    if len(text) == 0:
        return None
    
    text = text.partition('\n')
    if len(text) == 0:
        return None

    text = text[0].replace(" ","")
    if len(text) != len(cellsWithDigits):
        return None

    grid = []
    c = 0
    for i in range(0,len(cells)):
        row = []
        for j in range(0, len(cells[i])):
            if cells[i][j] is not None:
                row.append(text[c])
                c += 1
            else:
                row.append(0)
        grid.append(row)
    
    return grid


def main():
    if len(sys.argv) < 2:
        print("Give sudoku pic")
        return
    
    img = cv2.imread(sys.argv[1])
    if img is None:
        print("No such image found")
        return

    clean = cleanUp(img)
    if clean is None:
        print("Failed")
        return

    # cv2.imshow("clean",clean)
    # cv2.waitKey(0)

    cells = splitUp(clean)
    cells = highlightCells(cells)

    # printLocations(cells)

    # assertShape(cells)

    # print(cells)
    # saveCells(cells)
    grid = getDigits(cells)

    # assertShape(grid)
    # print(repr(text))
    
    # saveCells(cells)
    # cells = readDigits(cells)
    if grid is None:
        print("Unable to read numbers")
        return
    
    printCells(grid)


    # print("Done")
    # cv2.imshow("Clean",clean)
    # cv2.waitKey(0)
    # cells = splitUp(clean)

if __name__ == "__main__":
    main()