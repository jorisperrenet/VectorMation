"""Manim equivalent: MovingAround -- chain of shift, set_fill, scale, rotate."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/moving_around')
canvas.set_background()
square = Rectangle(200, 200, fill='#58C4DD', fill_opacity=1)
square.center_to_pos(posx=960, posy=540)
square.shift(dx=-200, start=0, end=1)
square.set_color(1, 2, '#FF862F')
square.scale(0.3, 2, 3)
square.rotate_by(3, 4, 23)

canvas.add_objects(square)
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/moving_around.mp4', fps=30)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
