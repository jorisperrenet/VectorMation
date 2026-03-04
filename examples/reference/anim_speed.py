"""Animation timing -- same motion at different durations."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

labels = ['1 second', '2 seconds', '4 seconds']
durations = [1, 2, 4]
colors = ['#E74C3C', '#3498DB', '#2ECC71']

for i, (label, dur, color) in enumerate(zip(labels, durations, colors)):
    y = 270 + i * 270
    txt = Text(label, x=100, y=y, font_size=32, fill=color)
    c = Circle(r=25, cx=400, cy=y, fill=color, fill_opacity=0.8)
    c.shift(dx=800, start=0.5, end=0.5 + dur)
    v.add(txt, c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/anim_speed.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
