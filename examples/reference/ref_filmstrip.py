"""Filmstrip storyboard display."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

strip = Filmstrip(
    labels=['Intro', 'Setup', 'Conflict', 'Climax', 'Resolution'],
    x=185, y=440, frame_width=260, frame_height=160, spacing=30,
)

v.add(strip)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_filmstrip.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
