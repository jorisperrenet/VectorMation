"""Various shapes bouncing with gravity, walls, and collisions."""
import random
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()

duration = 8
rng = random.Random(42)

title = Text(text='Bouncing Objects', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

space = PhysicsSpace(gravity=(0, 800), dt=1/120)
space.add_walls(left=60, right=1860, top=60, bottom=1020)

walls = [
    Line(x1=60, y1=1020, x2=1860, y2=1020, stroke='#555', stroke_width=2),
    Line(x1=60, y1=60, x2=1860, y2=60, stroke='#555', stroke_width=2),
    Line(x1=60, y1=60, x2=60, y2=1020, stroke='#555', stroke_width=2),
    Line(x1=1860, y1=60, x2=1860, y2=1020, stroke='#555', stroke_width=2),
]

colors = [
    '#FF6B6B', '#58C4DD', '#83C167', '#FFFF00', '#9B59B6',
    '#FF9F43', '#E74C3C', '#1ABC9C', '#E84393', '#6C5CE7',
    '#00CEC9', '#FD79A8', '#A29BFE', '#FFEAA7', '#55E6C1',
]


def make_random(i):
    """Create a random shape with random size, position, and velocity."""
    size = rng.randint(15, 40)
    cx = rng.randint(80 + size, 1840 - size)
    cy = rng.randint(80 + size, 500)
    vx, vy = rng.randint(-300, 300), rng.randint(-400, 100)
    color = colors[i % len(colors)]
    style = dict(fill=color, fill_opacity=0.85, stroke=lighten(color, 0.3), stroke_width=2)
    kind = rng.choice([
        'circle', 'ellipse', 'star',
        'triangle', 'pentagon', 'hexagon', 'octagon',
        'diamond', 'wedge', 'annular_sector',
    ])

    if kind == 'circle':
        obj = Circle(r=size, cx=cx, cy=cy, **style)
    elif kind == 'ellipse':
        rx, ry = size, rng.randint(int(size * 0.5), int(size * 0.8))
        obj = Ellipse(rx=rx, ry=ry, cx=cx, cy=cy, **style)
    elif kind == 'star':
        obj = Star(outer_radius=size, inner_radius=size * 0.45, cx=cx, cy=cy, **style)
    elif kind == 'diamond':
        s = size * 0.9
        obj = Polygon((cx, cy - s), (cx + s * 0.6, cy), (cx, cy + s), (cx - s * 0.6, cy), **style)
    elif kind == 'wedge':
        sweep = rng.randint(60, 150)
        start_a = rng.randint(0, 360)
        obj = Wedge(cx=cx, cy=cy, r=size, start_angle=start_a, end_angle=start_a + sweep, **style)
    elif kind == 'annular_sector':
        sweep = rng.randint(60, 150)
        start_a = rng.randint(0, 360)
        inner = size * 0.4
        obj = AnnularSector(inner_radius=inner, outer_radius=size, cx=cx, cy=cy,
                            start_angle=start_a, end_angle=start_a + sweep, **style)
    else:
        n = {'triangle': 3, 'pentagon': 5, 'hexagon': 6, 'octagon': 8}[kind]
        obj = RegularPolygon(n=n, radius=size, cx=cx, cy=cy, **style)

    space.add_body(obj, mass=(size / 20) ** 2, restitution=0.8, friction=0.02, vx=vx, vy=vy)
    return obj


objects = [make_random(i) for i in range(45)]

space.add_drag(coefficient=0.002)
space.simulate(duration=duration)

for obj in objects:
    obj.fadein(0, 0.3)

canvas.add_objects(*walls, title, *objects)

canvas.show()
