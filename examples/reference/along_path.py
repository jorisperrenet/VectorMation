"""Dot following a Bezier path."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

path_d = 'M 200,540 C 500,200 1400,200 1700,540'
guide = Path(path_d, stroke='#444', stroke_width=6, fill_opacity=0)
guide.fadein(start=0, end=0.5)

dot = Dot(cx=200, cy=540, r=12, fill='#FF6B6B')
dot.fadein(start=0, end=0.3)
dot.along_path(0.5, 3.5, path_d)

trail = dot.trace_path(start=0.5, end=3.5, stroke='#FF6B6B',
                       stroke_width=2, stroke_opacity=0.5)

v.add(guide, trail, dot)
if args.for_docs:
    v.export_video('docs/source/_static/videos/along_path.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
