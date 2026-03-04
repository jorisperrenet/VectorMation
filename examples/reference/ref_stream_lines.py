"""StreamLines for a swirl field."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

def swirl(x, y):
    dx, dy = x - 960, y - 540
    return (-dy, dx)

streams = StreamLines(swirl, n_steps=60, step_size=8,
                      stroke='#83C167', stroke_width=2)
v.add(streams)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_stream_lines.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
