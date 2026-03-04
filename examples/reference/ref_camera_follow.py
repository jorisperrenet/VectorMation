"""Camera follow example."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background(fill='#1a1a2e')

dot = Dot(cx=200, cy=540, r=14, fill='#58C4DD')
dot.fadein(start=0, end=0.3)
dot.shift(dx=1600, start=0.5, end=4.5)

line = Line(200, 540, 200, 540, stroke='#58C4DD', stroke_width=3)
line.p2.set_onward(0, dot.c.at_time)
v.camera_zoom(3, start=0, end=0.5)
v.camera_follow(dot, start=0.5, end=4.5)

v.add(line, dot)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_camera_follow.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
