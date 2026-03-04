"""PhysicsSpace: cloth simulation with wind."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import math
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

duration = 5

# Create a cloth: top row pinned, draping under gravity
cloth = Cloth(
    x=510, y=120,
    width=900, height=300,
    cols=18, rows=10,
    pin_top=True,
    stiffness=18,
    color='#58C4DD',
)

# Add a gentle sideways wind force
def wind_force(body, t):
    wind_x = 30 * math.sin(t * 1.2) + 10 * math.sin(t * 3.7)
    wind_y = 8 * math.cos(t * 2.5)
    return (wind_x, wind_y)

cloth.space.add_force(wind_force)
cloth.space.add_drag(coefficient=0.02)

cloth.simulate(duration=duration)

v.add(*cloth.objects())
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_physics_cloth.mp4', fps=30, end=duration)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=duration)
