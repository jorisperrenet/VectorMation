"""Updater-driven pulsing opacity."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

dot = Dot(cx=960, cy=540, r=40, fill='#83C167')
dot.add_updater(lambda obj, t: obj.styling.opacity.set_onward(
    0, 0.3 + 0.7 * abs(math.sin(t * 3))))

label = Text('opacity = sin(t)', x=960, y=650, font_size=28,
             fill='#888', text_anchor='middle')
label.fadein(start=0, end=0.5)

v.add(dot, label)
if args.for_docs:
    v.export_video('docs/source/_static/videos/updater.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
