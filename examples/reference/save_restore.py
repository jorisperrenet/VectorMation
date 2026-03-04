"""Save state, modify, then restore."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Circle(r=60, cx=960, cy=540, fill='#58C4DD', fill_opacity=0.8)
c.fadein(start=0, end=0.5)
c.save_state()

c.shift(dx=300, start=1, end=2)
c.set_color(1, 2, fill='#FF0000')
c.scale(1.5, start=1, end=2)

c.restore(start=3, end=4)

label = Text('restore to saved state at t=3', x=960, y=700,
             font_size=28, fill='#888', text_anchor='middle')
label.fadein(start=0, end=0.5)

v.add(c, label)
if args.for_docs:
    v.export_video('docs/source/_static/videos/save_restore.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
