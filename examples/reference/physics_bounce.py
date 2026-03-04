"""Balls bouncing with walls."""
from vectormation.objects import *
from vectormation._physics import PhysicsSpace

v = VectorMathAnim()
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

v.show(end=6)
