from sudoku import sudoku_c

if __name__ == "__main__":
    sudoku = sudoku_c(3)
    #sudoku.Print()
    #sudoku.Draw(30, winName="sudoku")

    if 1:
        sudoku.Clear()

        #sudoku.Gen_SimpleBackdate(True)
        sudoku.Gen_LessPossFirst()
        #sudoku.Print()

        print()

    if 1:
        sudoku.Mask(0.7)
        #sudoku.Gen_SimpleBackdate(True)
        sudoku.Gen_LessPossFirst(True)
        #sudoku.Print()