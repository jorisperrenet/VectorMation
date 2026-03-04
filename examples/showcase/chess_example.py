from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()

# Create a chess board with the starting position
board = ChessBoard(size=640)
board.fadein(0, 1)

# Play the Italian Game opening
board.move_piece('e2', 'e4', 1, 2)   # 1. e4
board.move_piece('e7', 'e5', 2, 3)   # 1. ...e5
board.move_piece('g1', 'f3', 3, 4)   # 2. Nf3
board.move_piece('b8', 'c6', 4, 5)   # 2. ...Nc6
board.move_piece('f1', 'c4', 5, 6)   # 3. Bc4 (Italian Game)

canvas.add_objects(board)

canvas.show(end=6)
