"""SampleSpace with horizontal division."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

space = SampleSpace(width=800, height=500, x=560, y=290)
space.divide_horizontally(0.6, colors=('#58C4DD', '#FC6255'), labels=['P(A) = 0.6', 'P(B) = 0.4'])

v.add(space)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_sample_space.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
