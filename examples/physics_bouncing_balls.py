"""Multiple colored balls bouncing with gravity, walls, and ball-ball collisions."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import random
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/physics_bouncing_balls')
canvas.set_background()

duration = 8

# Title
title = Text(text='Bouncing Balls', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Set up physics space
space = PhysicsSpace(gravity=(0, 800), dt=1/120)

# Walls: floor, ceiling, left, right
space.add_wall(y=1020)   # floor
space.add_wall(y=60)     # ceiling
space.add_wall(x=60)     # left wall
space.add_wall(x=1860)   # right wall

# Visual wall lines
floor_line = Line(x1=60, y1=1020, x2=1860, y2=1020, stroke='#555', stroke_width=2)
ceiling_line = Line(x1=60, y1=60, x2=1860, y2=60, stroke='#555', stroke_width=2)
left_line = Line(x1=60, y1=60, x2=60, y2=1020, stroke='#555', stroke_width=2)
right_line = Line(x1=1860, y1=60, x2=1860, y2=1020, stroke='#555', stroke_width=2)

# Generate balls in a loop
rng = random.Random(42)
colors = [
    '#FF6B6B', '#58C4DD', '#83C167', '#FFFF00', '#9B59B6',
    '#FF9F43', '#E74C3C', '#1ABC9C', '#E84393', '#6C5CE7',
    '#00CEC9', '#FD79A8', '#A29BFE', '#FFEAA7', '#55E6C1',
    '#F8A5C2', '#778BEB', '#CF6A87', '#63CDDA', '#EA8685',
]
n_balls = 40

balls = []
for i in range(n_balls):
    r = rng.randint(10, 35)
    cx = rng.randint(80 + r, 1840 - r)
    cy = rng.randint(80 + r, 600)
    vx = rng.randint(-300, 300)
    vy = rng.randint(-400, 100)
    mass = (r / 20) ** 2  # mass proportional to area
    color = colors[i % len(colors)]

    ball = Circle(r=r, cx=cx, cy=cy, fill=color, fill_opacity=0.85,
                  stroke=lighten(color, 0.3), stroke_width=2)
    space.add_body(ball, mass=mass, restitution=0.85, friction=0.02, vx=vx, vy=vy)
    balls.append(ball)

# Add a small amount of drag so things don't go on forever
space.add_drag(coefficient=0.002)

# Run the simulation
space.simulate(duration=duration)

# Fade in all balls
for ball in balls:
    ball.fadein(0, 0.3)

# Add everything to canvas
canvas.add_objects(
    floor_line, ceiling_line, left_line, right_line,
    title, *balls,
)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/physics_bouncing_balls.mp4', fps=30, end=8)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=8)
