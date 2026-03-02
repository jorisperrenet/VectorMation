import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/chess')
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

if args.verbose:
    canvas.export_video('docs/source/_static/videos/chess_example.mp4', fps=30, end=6)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
