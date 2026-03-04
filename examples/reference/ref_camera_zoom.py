"""Camera zoom example."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background(fill='#1a1a2e')

c1 = Circle(r=60, cx=500, cy=400, fill='#58C4DD', fill_opacity=0.8)
c2 = Circle(r=60, cx=1420, cy=640, fill='#E74C3C', fill_opacity=0.8)
c1.fadein(start=0, end=0.5)
c2.fadein(start=0, end=0.5)

v.camera_zoom(2.5, start=1, end=2.5, cx=500, cy=400)
v.camera_reset(3.5, 5)

v.add(c1, c2)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_camera_zoom.mp4', fps=30, end=6)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=6)
