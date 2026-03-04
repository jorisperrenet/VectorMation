"""TexObject with colored parts."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

eq = TexObject(r'$$E = mc^2$$', font_size=80,
               t2c={'E': '#FF6666', 'm': '#66FF66', 'c': '#6666FF'})
eq.center_to_pos()
eq.write(start=0, end=2)

v.add(eq)
if args.for_docs:
    v.export_video('docs/source/_static/videos/tex.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
