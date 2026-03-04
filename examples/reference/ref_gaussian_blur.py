"""Gaussian blur applied to shapes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

sharp = Circle(r=100, cx=700, cy=540, fill='#58C4DD', fill_opacity=0.9, stroke='#FFFFFF', stroke_width=2)

blurred = Circle(r=100, cx=1220, cy=540, fill='#FF6B6B', fill_opacity=0.9, stroke='#FFFFFF', stroke_width=2)
from vectormation._base_helpers import _wrap_to_svg
_wrap_to_svg(blurred, lambda inner, t:
    "<g filter='url(#gblur)'><defs><filter id='gblur' x='-50%' y='-50%' width='200%' height='200%'>"
    "<feGaussianBlur stdDeviation='6'/></filter></defs>" + inner + "</g>", 0)

v.add(sharp, blurred)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_gaussian_blur.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
