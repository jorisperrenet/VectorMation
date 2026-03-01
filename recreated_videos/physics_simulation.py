"""Physics Simulation Demo — PhysicsSpace, Body, Spring, Cloth, Wall.

Showcases the built-in physics engine: bouncing balls under gravity,
spring-connected bodies oscillating, and a cloth mesh draping.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/physics_simulation')
canvas.set_background()

T = 12.0

# -- Colors -------------------------------------------------------------------
CYAN    = '#58C4DD'
GREEN   = '#83C167'
YELLOW  = '#FFFF00'
RED     = '#FC6255'
ORANGE  = '#F5A623'
WHITE   = '#FFFFFF'
GREY    = '#888888'

# =============================================================================
# Phase 1 (0-5s): Bouncing balls under gravity
# =============================================================================
p1_title = Text(text='Bouncing Balls', x=960, y=60, font_size=40,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=0)
p1_title.fadein(0.0, 0.4)
p1_title.fadeout(4.5, 5.0)

p1_sub = Text(text='PhysicsSpace with Gravity and Walls', x=960, y=100,
              font_size=22, fill=GREY, stroke_width=0, text_anchor='middle',
              creation=0)
p1_sub.fadein(0.1, 0.5)
p1_sub.fadeout(4.5, 5.0)

# Floor and walls (visual)
floor_line = Line(x1=200, y1=850, x2=1720, y2=850,
                  stroke='#444', stroke_width=3, stroke_dasharray='8 4',
                  creation=0)
floor_line.fadein(0.0, 0.3)
floor_line.fadeout(4.5, 5.0)

left_wall_line = Line(x1=200, y1=150, x2=200, y2=850,
                      stroke='#444', stroke_width=3, stroke_dasharray='8 4',
                      creation=0)
left_wall_line.fadein(0.0, 0.3)
left_wall_line.fadeout(4.5, 5.0)

right_wall_line = Line(x1=1720, y1=150, x2=1720, y2=850,
                       stroke='#444', stroke_width=3, stroke_dasharray='8 4',
                       creation=0)
right_wall_line.fadein(0.0, 0.3)
right_wall_line.fadeout(4.5, 5.0)

# Create physics space
space1 = PhysicsSpace(gravity=(0, 600), dt=1/120, start=0.0)
space1.add_walls(left=200, right=1720, bottom=850)

# Create bouncing balls at different positions
ball_data = [
    (400, 200, CYAN, 25, 100, -50),
    (700, 250, GREEN, 20, -80, 30),
    (960, 180, YELLOW, 30, 50, -100),
    (1200, 300, RED, 22, -120, -20),
    (1500, 220, ORANGE, 18, 60, 80),
]

ball_objects = []
for bx, by, color, r, vx, vy in ball_data:
    ball = Circle(r=r, cx=bx, cy=by, fill=color, fill_opacity=0.9,
                  stroke='#222', stroke_width=2, creation=0)
    ball.fadein(0.2, 0.5)
    ball.fadeout(4.5, 5.0)
    space1.add_body(ball, mass=r/10, restitution=0.7, vx=vx, vy=vy)
    ball_objects.append(ball)

space1.simulate(duration=5.0)
canvas.add(p1_title, p1_sub, floor_line, left_wall_line, right_wall_line)
for b in ball_objects:
    canvas.add(b)

# =============================================================================
# Phase 2 (5-9s): Spring-connected bodies
# =============================================================================
p2_title = Text(text='Spring System', x=960, y=60, font_size=40,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=5.0)
p2_title.fadein(5.0, 5.4)
p2_title.fadeout(8.5, 9.0)

p2_sub = Text(text='Bodies Connected by Springs', x=960, y=100,
              font_size=22, fill=GREY, stroke_width=0, text_anchor='middle',
              creation=5.0)
p2_sub.fadein(5.1, 5.5)
p2_sub.fadeout(8.5, 9.0)

space2 = PhysicsSpace(gravity=(0, 300), dt=1/120, start=5.0)
space2.add_wall(y=900)

# Anchor point (fixed)
anchor_obj = Dot(cx=960, cy=200, r=8, fill=WHITE, creation=5.0)
anchor_obj.fadein(5.2, 5.5)
anchor_obj.fadeout(8.5, 9.0)
anchor_body = space2.add_body(anchor_obj, fixed=True)

# Hanging body
hang1_obj = Circle(r=25, cx=960, cy=450, fill=CYAN, fill_opacity=0.9,
                   stroke='#222', stroke_width=2, creation=5.0)
hang1_obj.fadein(5.2, 5.5)
hang1_obj.fadeout(8.5, 9.0)
hang1_body = space2.add_body(hang1_obj, mass=2.0, vx=200)

# Second hanging body
hang2_obj = Circle(r=20, cx=960, cy=650, fill=GREEN, fill_opacity=0.9,
                   stroke='#222', stroke_width=2, creation=5.0)
hang2_obj.fadein(5.3, 5.6)
hang2_obj.fadeout(8.5, 9.0)
hang2_body = space2.add_body(hang2_obj, mass=1.5, vx=-150)

# Springs
space2.add_spring(anchor_body, hang1_body, stiffness=2.0, damping=0.02)
space2.add_spring(hang1_body, hang2_body, stiffness=1.5, damping=0.02)

space2.simulate(duration=4.0)
canvas.add(p2_title, p2_sub, anchor_obj, hang1_obj, hang2_obj)

# Visual spring lines
spring_line1 = Line(x1=960, y1=200, x2=960, y2=450,
                    stroke=GREY, stroke_width=2, stroke_dasharray='6 3',
                    creation=5.0)
spring_line1.fadein(5.2, 5.5)
spring_line1.fadeout(8.5, 9.0)

spring_line2 = Line(x1=960, y1=450, x2=960, y2=650,
                    stroke=GREY, stroke_width=2, stroke_dasharray='6 3',
                    creation=5.0)
spring_line2.fadein(5.3, 5.6)
spring_line2.fadeout(8.5, 9.0)

canvas.add(spring_line1, spring_line2)

# =============================================================================
# Phase 3 (9-12s): Cloth simulation
# =============================================================================
p3_title = Text(text='Cloth Simulation', x=960, y=60, font_size=40,
                fill=WHITE, stroke_width=0, text_anchor='middle', creation=9.0)
p3_title.fadein(9.0, 9.4)
p3_title.fadeout(11.5, 12.0)

p3_sub = Text(text='Spring-Connected Particle Grid', x=960, y=100,
              font_size=22, fill=GREY, stroke_width=0, text_anchor='middle',
              creation=9.0)
p3_sub.fadein(9.1, 9.5)
p3_sub.fadeout(11.5, 12.0)

cloth = Cloth(x=560, y=200, width=800, height=400,
              cols=12, rows=8, pin_top=True, stiffness=2.0,
              color=CYAN, creation=9.0)
cloth.simulate(duration=3.0)

cloth_objs = cloth.objects()
for obj in cloth_objs:
    obj.fadein(9.2, 9.6)
    obj.fadeout(11.5, 12.0)

canvas.add(p3_title, p3_sub, *cloth_objs)

# -- Render -------------------------------------------------------------------
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
