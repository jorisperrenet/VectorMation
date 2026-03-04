"""Scramble decode effect."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

code = Text('ACCESS GRANTED', x=960, y=500, font_size=64,
            fill='#0f0', text_anchor='middle', font_family='monospace')
code.scramble(start=0, end=2)

v.add(code)
if args.for_docs:
    v.export_video('docs/source/_static/videos/scramble.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
