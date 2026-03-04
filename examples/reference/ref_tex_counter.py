"""TexCountAnimation: LaTeX-styled animated counter."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

counter = TexCountAnimation(0, 100, start=0, end=3, font_size=72)
counter.center_to_pos()

v.add(counter)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_tex_counter.mp4', fps=30, end=3.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3.5)
