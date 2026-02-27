"""Multiple colored balls bouncing with gravity, walls, and ball-ball collisions."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
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

# Ball configurations: (cx, cy, radius, color, vx, vy, mass)
ball_configs = [
    (300,  200, 40, '#FF6B6B', 200,  -100, 3.0),    # large red
    (600,  150, 30, '#58C4DD', -150, -200, 2.0),     # medium cyan
    (900,  300, 25, '#83C167', 300,  -50,  1.5),     # green
    (1200, 180, 35, '#FFFF00', -100, 100,  2.5),     # yellow
    (500,  400, 20, '#9B59B6', 250,  -300, 1.0),     # small purple
    (1400, 350, 28, '#FF9F43', -200, -150, 1.8),     # orange
    (800,  250, 22, '#E74C3C', 180,  50,   1.2),     # dark red
    (1100, 500, 32, '#1ABC9C', -80,  -250, 2.2),     # teal
    (350,  500, 18, '#E84393', 300,  -200, 0.8),     # pink
    (750,  600, 45, '#6C5CE7', 100,  -400, 4.0),     # large indigo
]

balls = []
for cx, cy, r, color, vx, vy, mass in ball_configs:
    ball = Circle(r=r, cx=cx, cy=cy, fill=color, fill_opacity=0.85,
                  stroke=lighten(color, 0.3), stroke_width=2)
    body = space.add_body(ball, mass=mass, restitution=0.85, friction=0.02,
                          vx=vx, vy=vy)
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

if not args.no_display:
    canvas.browser_display(start=0, end=duration, fps=args.fps, port=args.port,
                           hot_reload=True)
