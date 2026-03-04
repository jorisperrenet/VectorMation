"""CountAnimation example."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

counter = CountAnimation(0, 100, start=0, end=2, fmt='{:.0f}',
                         font_size=80, fill='#58C4DD', stroke_width=0,
                         text_anchor='middle')
counter.center_to_pos()
v.add(counter)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_count_anim.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
