"""Manim equivalent: VectorArrow -- arrow with labeled endpoints on a grid."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/vector_arrow')
canvas.set_background()
plane = NumberPlane()

# Arrow from origin (0,0) to (2,2) in logical coordinates
ox, oy = plane.coords_to_point(0, 0)
tx, ty = plane.coords_to_point(2, 2)
origin = Dot(cx=ox, cy=oy, r=8, fill='#fff', fill_opacity=1)
arrow = Arrow(x1=ox, y1=oy, x2=tx, y2=ty, stroke='#FFFFFF')

origin_text = Text('(0, 0)', font_size=36)
origin_text.center_to_pos(posx=ox, posy=oy + 50)
tip_text = Text('(2, 2)', font_size=36)
tip_text.center_to_pos(posx=tx + 50, posy=ty - 10)

canvas.add_objects(plane, origin, arrow, origin_text, tip_text)
if args.verbose:
    canvas.write_frame(0, 'docs/source/_static/videos/vector_arrow.svg')
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
