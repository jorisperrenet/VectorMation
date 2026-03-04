"""ZoomedInset with animated source position."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

# Small scene to magnify
sq = Square(side=60, x=330, y=470, fill='#4ECDC4', stroke='#FFFFFF', stroke_width=2)
circ = Circle(r=25, cx=500, cy=520, fill='#E84D60', stroke='#FFFFFF', stroke_width=2)
tri = EquilateralTriangle(side_length=50, cx=400, cy=600, fill='#FFFF00',
                          fill_opacity=0.7, stroke='#FFFF00', stroke_width=2)
v.add(sq, circ, tri)

inset = ZoomedInset(
    v,
    source=(300, 440, 160, 160),
    display=(800, 200, 500, 500),
    frame_color='#FFFF00', display_color='#FFFF00', frame_width=2,
)
v.add(inset)

# Animate the source region position
inset.move_source(400, 480, start=0.5, end=2.5)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_zoomed_inset_animated.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
