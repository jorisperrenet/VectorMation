"""Manim equivalent: GradientImageFromArray -- linear gradient with bounding rectangle."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
from vectormation.colors import LinearGradient
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/gradient_image')
canvas.set_background()

# Black-to-white linear gradient
grad = LinearGradient([('0%', '#000'), ('100%', '#fff')])
canvas.add_gradient(grad)

# Gradient rectangle centered on screen
rect = Rectangle(width=600, height=400, x=660, y=340, fill=grad, stroke_width=0)

# Green bounding rectangle
border = SurroundingRectangle(rect, buff=0, stroke='#00FF00', stroke_width=4,
                              fill_opacity=0)

canvas.add_objects(rect, border)
if args.verbose:
    canvas.write_frame(0, 'docs/source/_static/videos/gradient_image.svg')
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
