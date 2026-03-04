"""Balls bouncing with walls."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
from vectormation._physics import PhysicsSpace
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

space = PhysicsSpace(gravity=(0, 600))
space.add_walls()

colors = ['#58C4DD', '#FF6B6B', '#83C167', '#FFFF00', '#C55F73']
balls = []
for i in range(5):
    c = Circle(r=25, cx=300 + i * 150, cy=200, fill=colors[i])
    space.add_body(c, mass=1, vx=(i - 2) * 80, vy=-150)
    balls.append(c)

space.simulate(duration=6)

v.add(*balls)
if args.for_docs:
    v.export_video('docs/source/_static/videos/physics_bounce.mp4', fps=30, end=6)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=6)
