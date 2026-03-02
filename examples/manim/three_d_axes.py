"""Manim equivalent: FixedInFrameMObjectTest -- labeled 3D axes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/three_d_axes')
canvas.set_background()

axes = ThreeDAxes()

title = Text('3D Axes', font_size=48, fill='#fff', stroke_width=0)
title.to_corner('UL')

canvas.add_objects(axes, title)
if args.for_docs:
    canvas.write_frame(0, 'docs/source/_static/videos/three_d_axes.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
