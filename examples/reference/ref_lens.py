"""Lens with rays refracting through it."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

lens = Lens(cx=960, cy=540, height=400, focal_length=200, color='#58C4DD')
ray1 = Ray(x1=200, y1=440, angle=3, lenses=[lens], color='#F39C12', stroke_width=2)
ray2 = Ray(x1=200, y1=540, angle=0, lenses=[lens], color='#E74C3C', stroke_width=2)
ray3 = Ray(x1=200, y1=640, angle=-3, lenses=[lens], color='#2ECC71', stroke_width=2)

v.add(lens, ray1, ray2, ray3)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_lens.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
