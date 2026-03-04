"""Indicate and flash effects on objects."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

circle = Circle(r=80, cx=600, cy=540, fill='#E74C3C', fill_opacity=0.8)
circle.fadein(start=0, end=0.5)
circle.indicate(start=1, end=2, scale_factor=1.3)

square = Square(side=160, x=1240, y=460, fill='#3498DB', fill_opacity=0.8)
square.fadein(start=0, end=0.5)
square.flash(start=1, end=2, color='#FFFF00')

v.add(circle, square)
if args.for_docs:
    v.export_video('docs/source/_static/videos/indicate.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
