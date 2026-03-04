"""ChessBoard with default starting position."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

board = ChessBoard(size=600)

v.add(board)

v.show(end=0)
