"""Spring pendulum: a ball attached to a fixed anchor by a spring, oscillating under gravity."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/physics_spring')
canvas.set_background()

duration = 10

# Title
title = Text(text='Spring Pendulum', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Anchor point (fixed in space, top center)
anchor_x, anchor_y = 960, 180
anchor_dot = Dot(r=8, cx=anchor_x, cy=anchor_y, fill='#aaa', stroke='#fff', stroke_width=2)

# The bob: a colored circle attached by a spring
bob_start_x, bob_start_y = 1200, 350
bob = Circle(r=28, cx=bob_start_x, cy=bob_start_y,
             fill='#FF6B6B', fill_opacity=0.9,
             stroke=lighten('#FF6B6B', 0.3), stroke_width=3)

# Connecting line (spring visual) between anchor and bob
spring_line = Line(x1=anchor_x, y1=anchor_y,
                   x2=bob_start_x, y2=bob_start_y,
                   stroke='#FFFF00', stroke_width=2,
                   stroke_dasharray='8 4')

# Trace of the bob's path
trace = Trace(bob.c, start=0, end=duration,
              stroke='#FF6B6B', stroke_width=1.5, stroke_opacity=0.3)

# Physics space
space = PhysicsSpace(gravity=(0, 600), dt=1/120)

# Add the bob as a physics body with some initial sideways velocity
body = space.add_body(bob, mass=1.5, restitution=0.5, vx=-120, vy=0)

# Spring connecting the bob to the fixed anchor point
space.add_spring(
    (anchor_x, anchor_y),  # fixed anchor (tuple = static point)
    body,                   # the bob
    stiffness=1.2,
    rest_length=200,
    damping=0.03,
)

# Add light drag for realistic energy loss
space.add_drag(coefficient=0.003)

# Add a floor wall so the bob doesn't fly off screen
space.add_wall(y=1000)

# Run simulation
space.simulate(duration=duration)

# Bake the spring line endpoints to track anchor (static) and bob (dynamic)
# The anchor end stays fixed; the bob end follows the body trajectory
traj = body._trajectory
n = len(traj)
dt = space.dt
start_t = space.start

def bob_pos(t, _traj=traj, _start=start_t, _dt=dt, _n=n):
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

# Small decorative label
label = Text(text='k = 1.2, m = 1.5', x=960, y=1040,
             font_size=28, fill='#888', stroke_width=0, text_anchor='middle')
label.fadein(0.5, 1.5)

# Add everything to canvas
canvas.add_objects(trace, spring_line, anchor_dot, bob, title, label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/physics_spring.mp4', fps=30, end=10)
if not args.no_display:
    canvas.browser_display(start=0, end=duration, fps=args.fps, port=args.port,
                           hot_reload=True)
