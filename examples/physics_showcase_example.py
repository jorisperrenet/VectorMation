"""Physics engine showcase: bouncing balls, springs, and cloth simulation."""
from vectormation.objects import *

v = VectorMathAnim(duration=8)

# --- Bouncing balls ---
ball1 = Circle(r=20, cx=300, cy=200, fill='#E74C3C', fill_opacity=0.9)
ball2 = Circle(r=15, cx=600, cy=150, fill='#3498DB', fill_opacity=0.9)
ball3 = Circle(r=25, cx=900, cy=100, fill='#2ECC71', fill_opacity=0.9)

space = PhysicsSpace(gravity=(0, 500), dt=1/60)
b1 = Body(ball1, mass=2, restitution=0.7, vx=100, vy=0)
b2 = Body(ball2, mass=1, restitution=0.9, vx=-50, vy=50)
b3 = Body(ball3, mass=3, restitution=0.6, vx=0, vy=-100)
space.add(b1, b2, b3)
space.add_walls(left=50, right=1870, top=50, bottom=1030)
space.simulate(start=0, end=8)

# --- Spring connection ---
anchor = Circle(r=8, cx=1400, cy=100, fill='#fff', fill_opacity=1)
weight = Circle(r=25, cx=1400, cy=400, fill='#F39C12', fill_opacity=0.9)

space2 = PhysicsSpace(gravity=(0, 300), dt=1/60)
anchor_body = Body(anchor, fixed=True)
weight_body = Body(weight, mass=2, restitution=0.3)
spring = Spring(anchor_body, weight_body, rest_length=200, stiffness=50, damping=2)
space2.add(anchor_body, weight_body)
space2.add_spring(spring)
space2.add_walls(left=1200, right=1700, bottom=900)
space2.simulate(start=0, end=8)

v.add(ball1, ball2, ball3, anchor, weight)
v.render()
