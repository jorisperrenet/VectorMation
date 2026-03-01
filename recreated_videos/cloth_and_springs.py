"""Cloth simulation and spring-connected physics bodies demo."""
from vectormation.objects import (
    VectorMathAnim, Circle, Text, ORIGIN, parse_args,
    PhysicsSpace, Cloth,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/cloth_springs')

# Title
title = Text(text='Physics: Cloth & Springs', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: Spring-connected bouncing balls ──────────────────────
label1 = Text(text='Spring-Connected Bodies', x=480, y=110,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

space = PhysicsSpace(gravity=(0, 500), dt=1 / 120, start=0.5)

# Create three circles connected by springs
c1 = Circle(r=25, cx=300, cy=200, fill='#FF6B6B')
c2 = Circle(r=25, cx=480, cy=200, fill='#58C4DD')
c3 = Circle(r=25, cx=660, cy=200, fill='#83C167')

b1 = space.add_body(c1, mass=1.0, restitution=0.6)
b2 = space.add_body(c2, mass=1.5, restitution=0.6, vy=-200)
b3 = space.add_body(c3, mass=1.0, restitution=0.6)

# Springs connecting them
space.add_spring(b1, b2, stiffness=1.0, damping=0.05)
space.add_spring(b2, b3, stiffness=1.0, damping=0.05)

# Floor and walls
space.add_wall(y=550)  # floor
space.add_wall(x=130)  # left wall
space.add_wall(x=830)  # right wall

space.simulate(duration=5)
canvas.add(c1, c2, c3)

# ── Section 2: Cloth simulation ──────────────────────────────────────
label2 = Text(text='Cloth Simulation', x=1440, y=110,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label2)

cloth = Cloth(x=1090, y=180, width=700, height=400,
              cols=12, rows=8, pin_top=True,
              stiffness=2.5, color='#83C167', creation=0.5)
cloth.simulate(duration=5)
for obj in cloth.objects():
    canvas.add(obj)

# ── Section 3: Pendulum-like spring chain ────────────────────────────
label3 = Text(text='Spring Chain', x=ORIGIN[0], y=620,
              font_size=22, fill='#aaa', text_anchor='middle', creation=6)
canvas.add(label3)

space2 = PhysicsSpace(gravity=(0, 400), dt=1 / 120, start=6)

colors = ['#FF6B6B', '#FFFF00', '#83C167', '#58C4DD', '#FF79C6']
chain_balls = []
for i, c in enumerate(colors):
    ball = Circle(r=18, cx=760 + i * 80, cy=700, fill=c, creation=6)
    if i == 0:
        b = space2.add_body(ball, mass=1.0, fixed=True)
    else:
        b = space2.add_body(ball, mass=0.5, restitution=0.5)
    chain_balls.append((ball, b))

# Connect chain with springs
for i in range(len(chain_balls) - 1):
    space2.add_spring(chain_balls[i][1], chain_balls[i + 1][1],
                      stiffness=0.8, damping=0.03)

# Give the last ball a push
chain_balls[-1][1].vy = -300

space2.add_wall(y=1000)  # floor far below
space2.simulate(duration=5)

for ball, _ in chain_balls:
    canvas.add(ball)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 11,
                           fps=args.fps, port=args.port)
