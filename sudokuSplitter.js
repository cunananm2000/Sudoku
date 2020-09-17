let cellSize = 56
let border = 3

function focusGrid(img){
    // let img = cv.imread(imgInput)
    // console.log(gray.cols)
    // let graySize

    let gridSize = cellSize*9

    let rx = gridSize/img.cols
    let ry = gridSize/img.rows
    let r = Math.max(rx,ry)


    cv.resize(img,img,new cv.Size(),r,r)

    let gray = new cv.Mat()
    cv.cvtColor(img,gray,cv.COLOR_RGB2GRAY)
    cv.adaptiveThreshold(gray,gray,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,25,25)
    
    let blur = new cv.Mat()
    cv.GaussianBlur(gray,blur,new cv.Size(3,3),3)
    let edged = new cv.Mat()

    cv.Canny(blur,edged,100,180)

    let contours = new cv.MatVector();
    let hierarchy = new cv.Mat();

    cv.findContours(edged, contours, hierarchy, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE);

    if (contours.size == 0){
        console.log("No contours found")
        return null
    }

    // console.log(contours)

    let cntIndex = null
    let maxArea = 0
    for (let i = 0; i < contours.size(); i++){
        let area = cv.contourArea(contours.get(i))
        if (area > maxArea){
            maxArea = area
            cntIndex = i
        }
    }

    if (cntIndex == null){
        console.log("No contours of non-zero area")
        return null
    }

    let epsilon = 0.01*cv.arcLength(contours.get(cntIndex),true)
    let approx = new cv.Mat();
    cv.approxPolyDP(contours.get(cntIndex),approx,epsilon,true)
    // console.log(approx)
    approx = approx.data32S

    // cv.drawContours(img, contours, cntIndex, new cv.Scalar(255,0,0) , 1, cv.LINE_8, hierarchy, 100);

    // console.log(approx)

    if (approx.length != 8){
        console.log("No grid shape found")
        return null
    }

    let srcTri = cv.matFromArray(4, 1, cv.CV_32FC2, approx);
    let dstTri = cv.matFromArray(4, 1, cv.CV_32FC2, [0, 0, 0, gridSize, gridSize, gridSize, gridSize, 0]);
    let M = cv.getPerspectiveTransform(srcTri, dstTri);
    let dsize = new cv.Size(gray.rows, gray.cols);
    cv.warpPerspective(gray, gray, M, dsize, cv.INTER_LINEAR, cv.BORDER_CONSTANT, new cv.Scalar());

    // gray.delete()
    blur.delete()
    edged.delete()

    return gray
}

function splitUp(gridPic){
    // console.log(gridPic.rows)
    // console.log(gridPic.cols)
    let cells = []
    for (let i = 0; i < 9; i++){
        let row = []
        for (let j = 0; j < 9; j++){
            let cropped = new cv.Mat();
            let rect = new cv.Rect(cellSize*j+border,cellSize*i+border, cellSize-2*border,cellSize-2*border)
            // console.log(rect)
            cropped = gridPic.roi(rect);
            row.push(cropped)
        }
        cells.push(row)
    }
    return cells
}

function highlightDigit(cellPic){
    if (cellPic == null){
        return null
    }

    let img = new cv.Mat()
    cv.cvtColor(cellPic,img,cv.COLOR_GRAY2RGB)
    let gray = new cv.Mat()
    // cv.fastNlMeansDenoising(cellPic,gray,null,50,5,5)
    cv.bitwise_not(cellPic,gray)
    let stats = new cv.Mat()
    let labels = new cv.Mat()
    let centroid = new cv.Mat()
    cv.connectedComponentsWithStats(gray, labels, stats, centroid, 8, cv.CV_32S)
    // for (let i = 0; i < stats.rows; i++){
    //     console.log(stats.data32S[i*stats.rows + cv.CC_STAT_AREA])
    // }
    let largestLabel = -1
    let largestArea = -1
    for (let i = 1; i < stats.rows; i++){
        // console.log([stats.data32S[i*stats.rows + cv.CC_STAT_AREA],i])
        let area = stats.data32S[i*stats.cols + cv.CC_STAT_AREA]
        if (area > largestArea){
            largestArea = area
            largestLabel = i
        }
    }

    // console.log(labels)

    let width = cellPic.cols
    let height = cellPic.rows

    let cX = width/2.0
    let cY = height/2.0

    // console.log(Array.from(stats.data32S))
    // console.log([largestLabel,stats.rows])

    let largestInfo = Array.from(stats.data32S).splice(largestLabel*stats.cols,5)


    let x = largestInfo[0]
    let y = largestInfo[1]
    let w = largestInfo[2]
    let h = largestInfo[3]

    // console.log(largestInfo)

    let bX = x + w/2.0
    let bY = y + h/2.0

    if ((Math.abs(bX-cX) + Math.abs(bY-cY)) > 10 || w*h > 0.5*width*height){
        // console.log("No central blob")
        return null
    }

    
    let cropped = new cv.Mat();
    let rect = new cv.Rect(x,y,w,h)
    // console.log(rect)
    cropped = cellPic.roi(rect);

    return cropped
}

function highlightDigits(cellPics){
    for (let i = 0; i < cellPics.length; i++){
        for (let j = 0; j < cellPics[i].length; j++){
            cellPics[i][j] = highlightDigit(cellPics[i][j])
        }
    }
    return cellPics
}

function addPadding(img){
    cv.copyMakeBorder(img,img,10,10,2,2,cv.BORDER_CONSTANT,new cv.Scalar(255))
    return img
}

async function lineUp(imgList){
    minH = Math.min(...imgList.map(x => x.rows))
    imgList = imgList.map(x => addPadding(x))
    // imgList = imgList.map(x => cv.resize(x,x,new cv.Size(),Math.round(x.cols * minH / x.rows),minH))
    for (i in imgList){
        cv.resize(imgList[i],imgList[i],new cv.Size(Math.round(imgList[i].cols * minH / imgList[i].rows),minH))
    }

    // for (img of imgList){
    //     console.log(img.rows)
    // }

    let line = new cv.MatVector()
    for (img of imgList){
        line.push_back(img)
    }

    let compiled = new cv.Mat()
    cv.hconcat(line,compiled)

    cv.cvtColor (compiled, compiled, cv.COLOR_GRAY2RGB)
    return compiled
}

async function getDigits(cells){
    let cellsWithDigits = [].concat.apply([], cells);
    cellsWithDigits = cellsWithDigits.filter(x => x != null)
    let line = await lineUp(cellsWithDigits)
    // publicLine = line
    cv.imshow("output",line)
    line = document.getElementById("output").toDataURL();
    let worker = Tesseract.createWorker({
        logger: m => {}
    });
    let digits = await work(worker,line)
    // console.log(digits)

    if (digits == null || digits.length == 0){
        return null
    }

    digits = digits.split("\n")[0]
    if (digits.length == 0){
        return null
    }

    if ((digits.length != cellsWithDigits.length) || !(/^\d+$/.test(digits))){
        return null
    }

    // console.log(digits)

    let grid = []
    let c = 0
    for (let i = 0; i < cells.length; i++){
        let row = []
        for (let j = 0; j < cells.length; j++){
            if (cells[i][j] != null){
                row.push(parseInt(digits[c], 10))
                c += 1
            } else {
                row.push(0)
            }
        }
        grid.push(row)
    }
    return grid
}


const worker = Tesseract.createWorker({
logger: m => {}
});
    

async function work(worker,img) {
    // console.log(img)

    await worker.load();
    await worker.loadLanguage('eng');
    await worker.initialize('eng');

    await worker.setParameters({
        tessedit_char_whitelist: '0123456789',
        user_defined_dpi: '70'
    });

    let result = await worker.detect(img);
    // console.log(result.data);

    result = await worker.recognize(img);
    // console.log(result.data);
    

    await worker.terminate();

    // let digits = result.data

    return result.data.text
}

let publicCells = []
let publicLine = null

async function solvePic(img){
    if (img == null){
        console.log("No image")
        return false
    }

    let clean = focusGrid(img)
    if (clean == null){
        console.log("Failed to find grid")
        return false
    }

    let cells = splitUp(clean)
    publicCells = cells
    cells = highlightDigits(cells)
    
    let grid = await getDigits(cells)
    // console.log(grid)

    let mainGrid = new Grid(9,3,3)
    await mainGrid.load(grid)

    let result  = await mainGrid.solve()

    console.log(mainGrid.getGrid())
    // console.log(cells)

    // console.log(cells)

    // cv.imshow("output",clean)


}