const Status = {
    SOLVED: 'solved',
    IN_PROGRESS: 'in progress',
    IMPOSSIBLE: 'impossible'
}


class Grid {
    constructor(size,secW,secH,depth=0){
        this.size = size
        this.secW = secW
        this.secH = secH
        this.nSecsW = Math.floor(size/secW)
        this.nSecsH = Math.floor(size/secH)
        this.status = Status.IN_PROGRESS
        this.solved = []
        this.possible = []
        this.nSolved = 0
        this.queue = []
        this.depth = depth

        for (let i = 0; i < size; i++){
            let solvedRow = []
            let posRow = []
            for (let j = 0; j < size; j++){
                solvedRow.push(false)
                posRow.push(this.allNumbers())
            }
            this.solved.push(solvedRow)
            this.possible.push(posRow)
        }
    }

    async load(sampleGrid){
        if (sampleGrid.length != this.size){
            return false
        }
        for (let row of sampleGrid){
            if (row.length != this.size){
                return false
            }
        }

        for (let i = 0; i < this.size; i++){
            for (let j = 0; j < this.size; j++){
                let n = sampleGrid[i][j]
                if (n != 0){
                    this.addToQueue(n,i,j)
                }
            }
        }

        return true
    }

    allNumbers() {
        return [...Array(this.size).keys()].map(x => x + 1)
    }

    async writeIn(n,x,y){
        if (this.solved[x][y]){
            if (this.possible[x][y][0] != n){
                this.status = Status.IMPOSSIBLE
                this.nSolved = 0
                return false
            } else {
                return true
            }
        }

        this.solved[x][y] = true
        this.possible[x][y] = [n]
        this.nSolved++

        // console.log([this.depth,x,y,n])

        if (this.nSolved == this.size*this.size){
            this.status = Status.SOLVED
            return true
        }

        for (let j = 0; j < this.size; j++){
            if (j == y){
                continue
            }
            let index = this.possible[x][j].indexOf(n)
            if (index != -1){
                this.possible[x][j].splice(index,1)
                if (this.possible[x][j].length == 0){
                    this.status = Status.IMPOSSIBLE
                    this.nSolved = 0
                    return false
                } else if ((this.possible[x][j].length == 1) && !(this.solved[x][j])){
                    this.addToQueue(this.possible[x][j][0],x,j)
                }
            }
        }

        for (let i = 0; i < this.size; i++){
            if (i == x){
                continue
            }
            let index = this.possible[i][y].indexOf(n)
            if (index != -1){
                this.possible[i][y].splice(index,1)
                if (this.possible[i][y].length == 0){
                    this.status = Status.IMPOSSIBLE
                    this.nSolved = 0
                    return false
                } else if ((this.possible[i][y].length == 1) && !(this.solved[i][y])){
                    this.addToQueue(this.possible[i][y][0],i,y)
                }
            }
        }

        let tl = this.getTLofSec(x,y)
        for (let i = 0; i < this.secH; i++){
            for (let j = 0; j < this.secW; j++){
                if ((tl[0]+i == x) && (tl[1]+j == y)){
                    continue
                }
                let index = this.possible[tl[0]+i][tl[1]+j].indexOf(n)
                if (index != -1){
                    this.possible[tl[0]+i][tl[1]+j].splice(index,1)
                    if (this.possible[tl[0]+i][tl[1]+j].length == 0){
                        this.status = Status.IMPOSSIBLE
                        this.nSolved = 0
                        return false
                    } else if ((this.possible[tl[0]+i][tl[1]+j].length == 1) && !(this.solved[tl[0]+i][tl[1]+j])){
                        this.addToQueue(this.possible[tl[0]+i][tl[1]+j][0],tl[0]+i,tl[1]+j)
                    }
                }
            }
        }

        return true
    }

    getTLofSec(x,y){
        let i = this.secH * Math.floor(x/this.secH)
        let j = this.secW * Math.floor(y/this.secW)
        return [i,j]
    }

    addToQueue(n,x,y){
        this.queue.push([n,x,y])
    }

    async solveByElimination() {
        let currentSolved = this.nSolved
        for (let i = 0; i < this.size; i++){
            let row = []
            for (let j = 0; j < this.size; j++){
                row.push([i,j])
            }
            await this.solveGroup(row)
        }

        for (let j = 0; j < this.size; j++){
            let col = []
            for (let i = 0; i < this.size; i++){
                col.push([i,j])
            }
            await this.solveGroup(col)
        }

        for (let x = 0; x < this.nSecsH; x++){
            for (let y = 0; y < this.nSecsW; y++){
                let tlX = this.secH * x
                let tlY = this.secW * y
                let sec = []
                for (let i = 0; i < this.secH; i++){
                    for (let j = 0; j < this.secW; j++){
                        sec.push([tlX+i,tlY+j])
                    }
                }
                await this.solveGroup(sec)
            }
        }

        return (this.nSolved > currentSolved)
    }

    async solveGroup(group){
        let numbers = this.allNumbers()
        let emptys = []
        for (let pos of group){
            if (this.solved[pos[0]][pos[1]]){
                let index = numbers.indexOf(this.possible[pos[0]][pos[1]][0])
                if (index != -1){
                    numbers.splice(index,1)
                } else {
                    this.status = Status.IMPOSSIBLE
                    return false
                }
            } else {
                emptys.push(pos)
            }
        }

        for (let n of numbers){
            let chosen = null
            let found = false
            for (let pos of emptys){
                if (this.solved[pos[0]][pos[1]]){
                    continue
                }
                if (this.possible[pos[0]][pos[1]].includes(n)){
                    if (found){
                        found = false
                        break
                    } else {
                        chosen = pos
                        found = true
                    }
                }
            }
            if (found){
                await this.writeIn(n,chosen[0],chosen[1])
                await this.doQueue()
            }
        }

        return true
    }

    async doQueue() {
        let currentSolved = this.nSolved
        while (this.queue.length != 0){
            let curr = this.queue[0]
            this.writeIn(curr[0],curr[1],curr[2])
            this.queue.shift()
        }
        return (this.nSolved > currentSolved)
    }

    clone() {
        let newGrid = new Grid(this.size,this.secW,this.secH,this.depth+1)
        for (let i = 0; i < this.size; i++){
            for (let j = 0; j < this.size; j++){
                if (this.solved[i][j]){
                    newGrid.writeIn(this.possible[i][j][0],i,j)
                }
            }
        }
        return newGrid
    }

    getNatXY(x,y){
        if (this.solved[x][y]){
            return this.possible[x][y][0]
        } else {
            return 0
        }
    }

    getStatus(){
        return self.status
    }

    adapt(otherGrid){
        for (let i = 0; i < this.size; i++){
            for (let j = 0; j < this.size; j++){
                this.writeIn(otherGrid.getNatXY(i,j),i,j)
            }
        }
        this.status = otherGrid.getStatus()
    }

    async solveByGuess(){
        if (this.status != Status.IN_PROGRESS){
            return false
        }

        let changed = false
        for (let i = 0; i < this.size; i++){
            for (let j = 0; j < this.size; j++){
                if (!this.solved[i][j] && this.possible[i][j].length <= 4){
                    let works = -1
                    let nWorks = 0
                    // let attempts = []
                    for (let n of this.possible[i][j]) {
                        let tempGrid = this.clone()
                        tempGrid.writeIn(n,i,j)
                        // attempts.push(tempGrid)
                        // console.log(["Guessing",this.depth,n,i,j])
                        let status = await tempGrid.solve()
                        // console.log(JSON.parse(JSON.stringify(status)));
                        if (status === Status.SOLVED) {
                            // console.log("FOUND ONE THAT WORKS")
                            nWorks = 1
                            this.adapt(tempGrid)
                            this.status = Status.SOLVED
                            return true
                        } else if (status != Status.IMPOSSIBLE){
                            nWorks++
                            works = n
                            if (nWorks >= 2){
                                break
                            }
                        }
                    }

                    if (nWorks == 1){
                        changed = true
                        this.writeIn(works,i,j)
                        let progress = true
                        while (progress){
                            progress = await this.doQueue() || await this.solveByElimination()
                        }
                    }
                }
            }
        }

        return changed
    }

    async solve() {
        let progress = true
        while (progress){
            // console.log("going")
            progress = await this.doQueue() || await this.solveByElimination()
        }

        if (this.status == Status.IN_PROGRESS){
            // console.log("Done all logical steps")
            if (this.depth < 3){
                let dummy = await this.solveByGuess()
            }
        }

        return this.status
    }

    getGrid() {
        let ret = []
        for (let i = 0; i < this.size; i++){
            let row = []
            for (let j = 0; j < this.size; j++){
                if (this.solved[i][j]){
                    row.push(this.possible[i][j][0])
                } else {
                    row.push(0)
                }
            }
            ret.push(row)
        }
        return ret
    }
}

async function main(){
    let evilNumbers = [
        [0,0,0,5,0,8,0,2,0],
        [0,8,0,6,0,0,0,0,9],
        [0,3,5,4,0,0,7,0,0],
        [0,9,0,7,1,4,0,0,5],
        [0,0,0,0,0,0,9,0,0],
        [0,0,8,0,0,0,0,0,0],
        [0,0,0,0,0,0,1,5,0],
        [0,5,4,0,0,0,0,0,0],
        [6,0,3,0,0,2,0,0,8]
    ]
    let specNumbers = [
        [0,0,0,4,0,0,0,0,2],
        [0,0,3,0,5,0,4,0,0],
        [0,2,0,6,0,0,0,9,0],
        [1,0,7,0,0,0,0,0,0],
        [0,8,0,0,0,0,0,2,0],
        [0,0,0,0,0,0,9,0,5],
        [0,3,0,0,0,8,0,1,0],
        [0,0,2,0,1,0,5,0,0],
        [4,0,0,0,0,3,0,0,0]
    ]
    let easyNumbers = [
        [8,0,0,3,7,0,0,6,0],
        [0,9,4,0,2,0,0,0,0],
        [0,7,3,0,8,6,0,0,0],
        [0,0,0,8,1,4,0,0,5],
        [4,2,0,9,0,0,1,0,0],
        [7,1,8,0,0,2,3,0,4],
        [0,4,0,7,9,0,0,2,8],
        [5,0,2,1,0,0,0,0,0],
        [0,8,0,0,4,5,0,1,0]
    ]
    let ctcNumbers = [
        [1,0,0,4,0,0,7,0,0],
        [0,2,0,0,5,0,0,8,0],
        [0,0,3,0,0,6,0,0,9],
        [0,1,0,0,4,0,0,7,0],
        [0,0,2,0,0,5,0,0,8],
        [9,0,0,3,0,0,6,0,0],
        [7,0,0,0,0,8,0,0,2],
        [8,0,0,2,0,0,9,0,0],
        [0,9,0,0,7,0,0,1,0]
    ]
    let ctc2Numbers = [
        [0,0,0,0,0,0,0,1,2],
        [0,0,0,0,0,0,3,4,5],
        [0,0,0,0,0,3,6,7,0],
        [0,0,0,0,8,1,5,0,0],
        [0,0,0,7,5,4,0,0,0],
        [0,0,4,2,3,0,0,0,0],
        [0,6,7,9,0,0,0,0,0],
        [3,1,2,0,0,0,0,0,0],
        [8,5,0,0,0,0,0,0,0]
    ]
    let exp2Numbers = [
        [8,0,0,0,0,0,0,0,0],
        [0,0,3,6,0,0,0,0,0],
        [0,7,0,0,9,0,2,0,0],
        [0,5,0,0,0,7,0,0,0],
        [0,0,0,0,4,5,7,0,0],
        [0,0,0,1,0,0,0,3,0],
        [0,0,1,0,0,0,0,6,8],
        [0,0,8,5,0,0,0,1,0],
        [0,9,0,0,0,0,4,0,0],
    ]
    let worstNumbers = [
        [0,0,0,8,0,1,0,0,0],
        [0,0,0,0,0,0,4,3,0],
        [5,0,0,0,0,0,0,0,0],
        [0,0,0,0,7,0,8,0,0],
        [0,0,0,0,0,0,1,0,0],
        [0,2,0,0,3,0,0,0,0],
        [6,0,0,0,0,0,0,7,5],
        [0,0,3,4,0,0,0,0,0],
        [0,0,0,2,0,0,6,0,0]
    ]
    let mainGrid = new Grid(9,3,3)
    await mainGrid.load(ctc2Numbers)
    var t0 = performance.now()
    let result = await mainGrid.solve()
    var t1 = performance.now()
    // console.log("Took " + (t1 - t0) + " milliseconds.")
    // console.log(mainGrid.getGrid())
    // console.log(result)
    // return mainGrid.getGrid()
}