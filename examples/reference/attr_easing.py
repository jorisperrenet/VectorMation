"""Side-by-side circles shifting with different easings."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
from vectormation.easings import linear, smooth, ease_out_bounce
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

labels = ['linear', 'smooth', 'bounce']
easings = [linear, smooth, ease_out_bounce]
colors = ['#E74C3C', '#3498DB', '#2ECC71']

for i, (label, easing, color) in enumerate(zip(labels, easings, colors)):
    y = 270 + i * 270
    # Label
    txt = Text(label, x=100, y=y, font_size=36, fill=color)
    txt.fadein(start=0, end=0.3)
    # Circle that shifts right using this easing
    c = Circle(r=30, cx=400, cy=y, fill=color, fill_opacity=0.8)
    c.fadein(start=0, end=0.3)
    c.shift(dx=800, start=0.5, end=3, easing=easing)
    v.add(txt, c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/attr_easing.mp4', fps=30, end=3.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3.5)
