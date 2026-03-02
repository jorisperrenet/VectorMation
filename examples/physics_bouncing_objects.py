"""Various shapes bouncing with gravity, walls, and collisions."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import random
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/physics_bouncing_objects')
canvas.set_background()

duration = 8

title = Text(text='Bouncing Objects', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

space = PhysicsSpace(gravity=(0, 800), dt=1/120)

# Walls
space.add_wall(y=1020)
space.add_wall(y=60)
space.add_wall(x=60)
space.add_wall(x=1860)

floor_line = Line(x1=60, y1=1020, x2=1860, y2=1020, stroke='#555', stroke_width=2)
ceiling_line = Line(x1=60, y1=60, x2=1860, y2=60, stroke='#555', stroke_width=2)
left_line = Line(x1=60, y1=60, x2=60, y2=1020, stroke='#555', stroke_width=2)
right_line = Line(x1=1860, y1=60, x2=1860, y2=1020, stroke='#555', stroke_width=2)

rng = random.Random(42)

colors = [
    '#FF6B6B', '#58C4DD', '#83C167', '#FFFF00', '#9B59B6',
    '#FF9F43', '#E74C3C', '#1ABC9C', '#E84393', '#6C5CE7',
    '#00CEC9', '#FD79A8', '#A29BFE', '#FFEAA7', '#55E6C1',
]

objects = []

def random_vel():
    return rng.randint(-300, 300), rng.randint(-400, 100)

def random_pos(r=30):
    return rng.randint(80 + r, 1840 - r), rng.randint(80 + r, 500)

# Circles (10)
for i in range(10):
    r = rng.randint(15, 35)
    cx, cy = random_pos(r)
    vx, vy = random_vel()
    color = colors[i % len(colors)]
    obj = Circle(r=r, cx=cx, cy=cy, fill=color, fill_opacity=0.85,
                 stroke=lighten(color, 0.3), stroke_width=2)
    space.add_body(obj, mass=(r / 20) ** 2, restitution=0.85, friction=0.02, vx=vx, vy=vy)
    objects.append(obj)

# Squares / Rectangles (8)
for i in range(8):
    s = rng.randint(25, 50)
    w, h = s, rng.randint(int(s * 0.8), int(s * 1.2))  # near-square
    cx, cy = random_pos(max(w, h))
    vx, vy = random_vel()
    color = colors[(10 + i) % len(colors)]
    obj = Rectangle(x=cx - w / 2, y=cy - h / 2, width=w, height=h,
                    fill=color, fill_opacity=0.85,
                    stroke=lighten(color, 0.3), stroke_width=2, rx=4)
    space.add_body(obj, mass=(w * h) / 800, restitution=0.75, friction=0.03, vx=vx, vy=vy)
    objects.append(obj)

# Triangles (6)
for i in range(6):
    size = rng.randint(25, 45)
    cx, cy = random_pos(size)
    vx, vy = random_vel()
    color = colors[(18 + i) % len(colors)]
    obj = RegularPolygon(n=3, radius=size, cx=cx, cy=cy,
                         fill=color, fill_opacity=0.85,
                         stroke=lighten(color, 0.3), stroke_width=2)
    space.add_body(obj, mass=(size / 20) ** 2, restitution=0.8, friction=0.02, vx=vx, vy=vy)
    objects.append(obj)

# Pentagons (4)
for i in range(4):
    size = rng.randint(20, 35)
    cx, cy = random_pos(size)
    vx, vy = random_vel()
    color = colors[(24 + i) % len(colors)]
    obj = RegularPolygon(n=5, radius=size, cx=cx, cy=cy,
                         fill=color, fill_opacity=0.85,
                         stroke=lighten(color, 0.3), stroke_width=2)
    space.add_body(obj, mass=(size / 20) ** 2, restitution=0.8, friction=0.02, vx=vx, vy=vy)
    objects.append(obj)

# Stars (4)
for i in range(4):
    size = rng.randint(20, 35)
    cx, cy = random_pos(size)
    vx, vy = random_vel()
    color = colors[(28 + i) % len(colors)]
    obj = Star(outer_radius=size, inner_radius=size * 0.45, cx=cx, cy=cy, n=5,
               fill=color, fill_opacity=0.85,
               stroke=lighten(color, 0.3), stroke_width=2)
    space.add_body(obj, mass=(size / 20) ** 2, restitution=0.8, friction=0.02, vx=vx, vy=vy)
    objects.append(obj)

space.add_drag(coefficient=0.002)
space.simulate(duration=duration)

for obj in objects:
    obj.fadein(0, 0.3)

canvas.add_objects(
    floor_line, ceiling_line, left_line, right_line,
    title, *objects,
)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/physics_bouncing_objects.mp4', fps=30, end=8)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=8)
