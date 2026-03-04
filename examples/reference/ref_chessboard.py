"""ChessBoard with default starting position."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

board = ChessBoard(size=600)

v.add(board)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_chessboard.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
