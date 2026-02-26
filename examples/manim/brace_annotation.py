"""Manim equivalent: BraceAnnotation -- brace with text label."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/brace_annotation')
canvas.set_background()
# Manim: dot at [-2,-1] and [2,1] => centered on canvas
dot1 = Dot(cx=660, cy=690, fill='#fff', fill_opacity=1)
dot2 = Dot(cx=1260, cy=390, fill='#fff', fill_opacity=1)
line = Line(x1=660, y1=690, x2=1260, y2=390, stroke='#FF862F', stroke_width=8)
b1 = Brace(line, direction='down', label='Horizontal distance')
b2 = Brace(line, direction='right', label=r'$x-x_1$')

canvas.add_objects(line, dot1, dot2, b1, b2)
if args.verbose:
    canvas.write_frame(0, 'docs/source/_static/videos/brace_annotation.svg')
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
