"""PhysicsSpace: bouncing objects with walls."""
import random
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

duration = 6
rng = random.Random(42)

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
]

objects = []
for i in range(30):
    size = rng.randint(15, 35)
    cx = rng.randint(80 + size, 1840 - size)
    cy = rng.randint(80 + size, 500)
    vx, vy = rng.randint(-300, 300), rng.randint(-400, 100)
    color = colors[i % len(colors)]
    style = dict(fill=color, fill_opacity=0.85, stroke=lighten(color, 0.3), stroke_width=2)
    obj = Circle(r=size, cx=cx, cy=cy, **style)
    space.add_body(obj, mass=(size / 20) ** 2, restitution=0.8, friction=0.02, vx=vx, vy=vy)
    objects.append(obj)

space.add_drag(coefficient=0.002)
space.simulate(duration=duration)

v.add(*walls, *objects)

v.show(end=duration)
