"""Manim equivalent: MovingGroupToDestination -- move a group to align with a target."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/moving_group')
canvas.set_background()
d1 = Dot(cx=660, cy=540)
d2 = Dot(cx=760, cy=540)
d3 = Dot(cx=860, cy=540, fill='#FC6255')
d4 = Dot(cx=960, cy=540)
group = VCollection(d1, d2, d3, d4)

dest = Dot(cx=1200, cy=300, fill='#FFFF00')

# Shift the group so d3 (the red dot) ends up at dest
target_x, target_y = 1200, 300
ref_x, ref_y = d3.c.at_time(0)
group.shift(dx=target_x - ref_x, dy=target_y - ref_y, start=0.5, end=2)

canvas.add_objects(group, dest)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/moving_group.mp4', fps=30)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
