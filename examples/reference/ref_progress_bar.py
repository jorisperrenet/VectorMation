"""ProgressBar at 70% fill."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

bar = ProgressBar(width=600, height=35, x=660, y=520, fill_color='#58C4DD')
bar.set_progress(0.7)

v.add(bar)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_progress_bar.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
