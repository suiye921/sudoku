import numpy, random, copy, sys
import cv2

class sudoku_c:
    class summary_c:
        def __init__(self, rank):
            self.rank = rank
            self.sideLen = rank * rank
            self.bankNum = rank * rank

            self.loNumSetInRow = [set() for i in range(self.sideLen)]
            self.loNumSetInCol = [set() for i in range(self.sideLen)]
            self.loNumSetInBank = [set() for i in range(self.bankNum)]

        def Clear(self):
            self.loNumSetInBank.clear()
            self.loNumSetInCol.clear()
            self.loNumSetInRow.clear()

        def Copy(self, summ):
            assert isinstance(summ, sudoku_c.summary_c)
            assert summ.rank == self.rank

            self.loNumSetInRow = copy(summ.loNumSetInRow)
            self.loNumSetInCol = copy(summ.loNumSetInCol)
            self.loNumSetInBank = copy(summ.loNumSetInBank)

        def AssertPosPlate(self, x, y, bankIdx):
            assert x >= 0 and x < self.sideLen
            assert y >= 0 and y < self.sideLen
            assert bankIdx >= 0 and bankIdx < self.bankNum

        def CheckNum(self, x, y, bankIdx, num):
            self.AssertPosPlate(x, y, bankIdx)

            if num < 1 or num > self.sideLen:
                return False

            if num in self.loNumSetInRow or \
                    num in self.loNumSetInCol or \
                    num in self.loNumSetInBank:
                return False
            else:
                return True

        def Add(self, x, y, bankIdx, num):
            self.AssertPosPlate(x, y, bankIdx)

            isValid = self.CheckNum(x, y, bankIdx, num)

            if isValid:
                self.loNumSetInRow[y].add(num)
                self.loNumSetInCol[x].add(num)
                self.loNumSetInBank[bankIdx].add(num)

            return isValid

        def Remove(self, x, y, bankIdx, num):
            self.AssertPosPlate(x, y, bankIdx)

            self.loNumSetInRow[y].remove(num)
            self.loNumSetInCol[x].remove(num)
            self.loNumSetInBank[bankIdx].remove(num)

        def GetPossibleNum(self, x, y, bankIdx):
            sPossibleNum = set(range(1, self.sideLen + 1))

            sPossibleNum -= self.loNumSetInRow[y]
            sPossibleNum -= self.loNumSetInCol[x]
            sPossibleNum -= self.loNumSetInBank[bankIdx]

            if len(sPossibleNum) > 0:
                return tuple(sPossibleNum)
            else:
                return None

    class stepRecord_c:
        def __init__(self, numIdx, tPossibleNum):
            assert len(tPossibleNum) > 0

            self.numIdx = numIdx
            self.loPossibleNum = list(tPossibleNum)

        def GetPossibleNum(self):
            possibleNumSize = len(self.loPossibleNum)
            if possibleNumSize > 0:
                possibleNumIdx = random.randint(0, possibleNumSize-1)

                possibleNum = self.loPossibleNum[possibleNumIdx]
                self.loPossibleNum.pop(possibleNumIdx)

                return possibleNum
            else:
                return None

    def __init__(self, rank = 3):
        assert isinstance(rank, int)
        assert rank >= 2

        self.rank = rank
        self.sideLen = rank * rank
        self.bankSize = rank * rank
        self.bankNum = rank * rank
        self.numSize = self.bankSize * self.bankNum

        self.loNum = list(range(1, self.numSize + 1))

    def Pos2NumIdx(self, x, y):
        numIdx = y * self.sideLen + x
        return numIdx

    def NumIdx2Pos(self, numIdx):
        y = numIdx // self.sideLen
        x = numIdx % self.sideLen

        return (x, y)

    def Pos2BankIdx(self, x, y):
        bankIdx = y // self.rank * self.rank + x // self.rank
        return bankIdx

    def NumIdx2PosPlate(self, numIdx):
        x, y = self.NumIdx2Pos(numIdx)
        bankIdx = self.Pos2BankIdx(x, y)

        return (x, y, bankIdx)

    def Clear(self):
        for numIdx in range(self.numSize):
            self.loNum[numIdx] = None

    def Print(self, stream = sys.stdout):
        for numIdx, num in enumerate(self.loNum):
            if num is not None:
                stream.write("%d" % num)
            else:
                stream.write("X")
            if numIdx % self.sideLen == self.sideLen - 1:
                stream.write("\r\n")
            else:
                stream.write("\t")

    def Draw(self, cellSideLen = 50, winName = None, sOriNumIdx = None):
        width = self.sideLen * cellSideLen + 2
        height = self.sideLen * cellSideLen + 2

        drawMat = numpy.full((width, height, 3), 255, numpy.uint8)
        for i in range(self.sideLen+1):
            px = cellSideLen * i
            py = cellSideLen * i

            if i % self.rank == 0:
                cv2.line(drawMat, (px, 0), (px, height-1), (0, 0, 0), 2)
                cv2.line(drawMat, (0, py), (width-1, py), (0, 0, 0), 2)
            else:
                cv2.line(drawMat, (px, 0), (px, height - 1), (0, 0, 0), 1)
                cv2.line(drawMat, (0, py), (width - 1, py), (0, 0, 0), 1)


        fontFace = cv2.FONT_HERSHEY_SIMPLEX
        fontHeight = int(cellSideLen * 0.3)
        fontScale = cv2.getFontScaleFromHeight(fontFace, fontHeight, 1)
        fontThickness = 2

        for numIdx, num in enumerate(self.loNum):
            x, y, bankIdx = self.NumIdx2PosPlate(numIdx)

            if num is not None:
                numStr = "%d" % num
            else:
                numStr = " "

            textSize, baseLine = cv2.getTextSize(numStr, fontFace, fontScale, fontThickness)
            px = cellSideLen * x + (cellSideLen - textSize[0]) // 2
            py = cellSideLen * y + fontHeight + (cellSideLen - fontHeight) // 2

            numColor = (0, 0, 0)
            if sOriNumIdx is not None:
                if numIdx in sOriNumIdx:
                    numColor = (0, 0, 255)

            cv2.putText(drawMat, numStr, (px, py), fontFace, fontScale, numColor, fontThickness)

        if winName != None:
            cv2.imshow(winName, drawMat)
            cv2.waitKey()
            cv2.destroyWindow(winName)

        return drawMat

    def BuildSumm(self):
        summ = sudoku_c.summary_c(self.rank)

        isValid = True
        for x in range(self.sideLen):
            if not isValid:
                break
            for y in range(self.sideLen):
                bankIdx = self.Pos2BankIdx(x, y)
                numIdx = self.Pos2NumIdx(x, y)

                num = self.loNum[numIdx]
                if num is not None:
                    if not summ.Add(x, y, bankIdx, num):
                        isValid = False
                        break

        if isValid:
            return summ
        else:
            return None

    def CheckValid(self):
        return self.BuildSumm() is not None

    def BackdateStepRecord(self, loStepRecord, summ):
        noSolution = False
        numIdx = -1
        while True:
            if len(loStepRecord) > 0:
                preStepRecord = loStepRecord[-1]
                assert isinstance(preStepRecord, sudoku_c.stepRecord_c)

                oldNumIdx = preStepRecord.numIdx
                oldNum = self.loNum[oldNumIdx]
                oldX, oldY, oldBankIdx = self.NumIdx2PosPlate(oldNumIdx)

                summ.Remove(oldX, oldY, oldBankIdx, oldNum)

                newNum = preStepRecord.GetPossibleNum()
                self.loNum[oldNumIdx] = newNum

                if newNum is not None:
                    summ.Add(oldX, oldY, oldBankIdx, newNum)
                    numIdx = oldNumIdx + 1
                    break
                else:
                    loStepRecord.pop(-1)
            else:
                noSolution = True
                break

        return (not noSolution, numIdx)


    def Gen_SimpleBackdate(self, showProgress = False):
        summ = self.BuildSumm()
        assert summ is not None

        winName = "sudoku_%d_progress" % self.rank

        sOriNumIdx = set()
        for numIdx, num in enumerate(self.loNum):
            if num is not None:
                sOriNumIdx.add(numIdx)

        numIdx = 0
        noSolution = False
        loStepRecord = list()
        while (numIdx < self.numSize) and (not noSolution):
            num = self.loNum[numIdx]
            if num is None:
                x, y, bankIdx = self.NumIdx2PosPlate(numIdx)
                tPossibleNum = summ.GetPossibleNum(x, y, bankIdx)
                if tPossibleNum is not None:
                    stepRecord = sudoku_c.stepRecord_c(numIdx, tPossibleNum)
                    newNum = stepRecord.GetPossibleNum()

                    loStepRecord.append(stepRecord)
                    self.loNum[numIdx] = newNum

                    summ.Add(x, y, bankIdx, newNum)
                else:
                    retVal, numIdx = self.BackdateStepRecord(loStepRecord, summ)
                    noSolution = not retVal
            else:
                numIdx += 1

            if showProgress:
                sudokuMat = self.Draw(sOriNumIdx = sOriNumIdx)
                cv2.imshow(winName, sudokuMat)
                cv2.waitKey(10)

        if showProgress:
            cv2.waitKey()
            cv2.destroyWindow(winName)

        return not noSolution

    def Gen_LessPossFirst(self, showProgress=False):
        summ = self.BuildSumm()
        assert summ is not None

        sOriNumIdx = set()
        for numIdx, num in enumerate(self.loNum):
            if num is not None:
                sOriNumIdx.add(numIdx)

        winName = "sudoku_%d_progress" % self.rank

        numIdx = 0
        loStepRecord = list()

        minPossNumIdx = -1
        tMinPossNum = None

        noSolution = False
        hasEmptyCell = False
        hasImpossCell = False
        while not noSolution:
            num = self.loNum[numIdx]
            if num is None:
                hasEmptyCell = True

                x, y, bankIdx = self.NumIdx2PosPlate(numIdx)
                tPossibleNum = summ.GetPossibleNum(x, y, bankIdx)

                if tPossibleNum is not None:
                    if minPossNumIdx == -1:
                        minPossNumIdx = numIdx
                        tMinPossNum = tPossibleNum
                    else:
                        if len(tPossibleNum) < len(tMinPossNum):
                            minPossNumIdx = numIdx
                            tMinPossNum = tPossibleNum

                    if len(tPossibleNum) == 1:
                        numIdx = self.numSize   # end this loop
                else:
                    hasImpossCell = True
                    numIdx = self.numSize   # end this loop

            numIdx += 1

            if numIdx >= self.numSize:
                if hasImpossCell:
                    retVal = self.BackdateStepRecord(loStepRecord, summ)[0]
                    noSolution = not retVal

                    if noSolution:
                        pass
                elif hasEmptyCell:
                    assert minPossNumIdx != -1
                    stepRecord = sudoku_c.stepRecord_c(minPossNumIdx, tMinPossNum)
                    newNum = stepRecord.GetPossibleNum()

                    self.loNum[minPossNumIdx] = newNum

                    loStepRecord.append(stepRecord)

                    x, y, bankIdx = self.NumIdx2PosPlate(minPossNumIdx)
                    summ.Add(x, y, bankIdx, newNum)
                else:
                    break

                numIdx = 0
                hasEmptyCell = False
                hasImpossCell = False
                if minPossNumIdx != -1:
                    minPossNumIdx = -1
                    tMinPossNum = None

                if showProgress:
                    sudokuMat = self.Draw(sOriNumIdx=sOriNumIdx)
                    cv2.imshow(winName, sudokuMat)
                    cv2.waitKey(10)

        if showProgress:
            cv2.waitKey()
            cv2.destroyWindow(winName)


        return not noSolution

    def Mask(self, maskRate = 0.5):
        assert maskRate >= 0.0 and maskRate <= 1.0

        for numIdx, num in enumerate(self.loNum):
            if num is not None:
                if random.random() < maskRate:
                    self.loNum[numIdx] = None




if __name__ == "__main__":
    sudoku = sudoku_c(4)
    #sudoku.Print()
    #sudoku.Draw(30, winName="sudoku")

    if 1:
        sudoku.Clear()

        #sudoku.Gen_SimpleBackdate(True)
        sudoku.Gen_LessPossFirst(True)
        sudoku.Print()

        print()

    if 1:
        sudoku.Mask(0.9)
        #sudoku.Gen_SimpleBackdate(True)
        sudoku.Gen_LessPossFirst(True)
        sudoku.Print()




