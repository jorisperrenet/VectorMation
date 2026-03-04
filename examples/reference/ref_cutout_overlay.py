"""Rectangular cutout overlay (Cutout class)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

title = Text('Important', x=960, y=400, font_size=72, fill='#FFFFFF', text_anchor='middle')
subtitle = Text('Focus here', x=960, y=700, font_size=36, fill='#aaa', text_anchor='middle')
v.add(title, subtitle)

cutout = Cutout(opacity=0.8, rx=12, ry=12)
cutout.surround(title, buff=30)
v.add(cutout)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_cutout_overlay.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
