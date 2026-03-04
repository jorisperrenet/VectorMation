"""PhysicsSpace: spring pendulum with visual spring line."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

duration = 5

# Anchor point (fixed in space, top center)
anchor_x, anchor_y = 960, 150
anchor_dot = Dot(r=8, cx=anchor_x, cy=anchor_y, fill='#aaa', stroke='#fff', stroke_width=2)

# The bob: a colored circle attached by a spring
bob = Circle(r=28, cx=1300, cy=250,
             fill='#FF6B6B', fill_opacity=0.9,
             stroke=lighten('#FF6B6B', 0.3), stroke_width=3)

# Connecting line (spring visual) between anchor and bob
spring_line = Line(x1=anchor_x, y1=anchor_y,
                   x2=1300, y2=250,
                   stroke='#FFFF00', stroke_width=2,
                   stroke_dasharray='8 4')

# Physics space
space = PhysicsSpace(gravity=(0, 500), dt=1/120)

# Add the bob as a physics body
body = space.add_body(bob, mass=1.5, restitution=0.5, vx=-150, vy=0)

# Spring connecting the bob to the fixed anchor point
space.add_spring(
    (anchor_x, anchor_y),  # fixed anchor
    body,
    stiffness=8,
    rest_length=250,
    damping=0.3,
)

space.add_drag(coefficient=0.001)
space.add_wall(y=1000)
space.simulate(duration=duration)

# Bake the spring line endpoints to track the bob
traj = body._trajectory
n = len(traj)
dt_sim = space.dt
start_t = space.start

def bob_pos(t, _traj=traj, _start=start_t, _dt=dt_sim, _n=n):
    elapsed = t - _start
    if elapsed <= 0:
        return _traj[0]
    idx = elapsed / _dt
    i = int(idx)
    if i >= _n - 1:
        return _traj[-1]
    frac = idx - i
    x1, y1 = _traj[i]
    x2, y2 = _traj[i + 1]
    return (x1 + (x2 - x1) * frac, y1 + (y2 - y1) * frac)

spring_line.p2.set_onward(0, bob_pos)

v.add(spring_line, anchor_dot, bob)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_physics_spring.mp4', fps=30, end=duration)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=duration)
