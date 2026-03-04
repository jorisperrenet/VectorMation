"""ClipPath clipping a rectangle with a circle."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

clip = ClipPath(Circle(r=150, cx=960, cy=540))
v.add_def(clip)

rect = Rectangle(500, 500, fill='#58C4DD', fill_opacity=0.9,
                 stroke='#FFFFFF', stroke_width=3,
                 clip_path=clip.clip_ref())
rect.center_to_pos(posx=960, posy=540)

# Show the clip circle outline for reference
outline = Circle(r=150, cx=960, cy=540, fill_opacity=0,
                 stroke='#FFFF00', stroke_width=2, stroke_dasharray='8,6')
v.add(rect, outline)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_clip_path.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
