#!/usr/bin/env python3
"""Generate angle / right-angle parameter diagram."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 440, 260
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

# --- Angle indicator (left side) ---
VX, VY = 120, 180
LEN = 120
P1X, P1Y = VX + LEN, VY
P2X, P2Y = VX + int(LEN * math.cos(math.radians(55))), VY - int(LEN * math.sin(math.radians(55)))

# Rays
canvas.add_objects(
    Line(x1=VX, y1=VY, x2=P1X, y2=P1Y, stroke='#58C4DD', stroke_width=2),
    Line(x1=VX, y1=VY, x2=P2X, y2=P2Y, stroke='#58C4DD', stroke_width=2),
)

# Angle arc
canvas.add_objects(
    Arc(cx=VX, cy=VY, r=36, start_angle=0, end_angle=55,
        fill_opacity=0, stroke='#f9e2af', stroke_width=2),
)

# Labels
canvas.add_objects(
    Dot(r=4, cx=VX, cy=VY, fill='#f38ba8', stroke_width=0),
    Text('vertex', x=VX - 42, y=VY + 18, font_size=11, fill='#f38ba8'),
    Dot(r=3, cx=P1X, cy=P1Y, fill='#a6e3a1', stroke_width=0),
    Text('p1', x=P1X + 5, y=P1Y + 15, font_size=11, fill='#a6e3a1'),
    Dot(r=3, cx=P2X, cy=P2Y, fill='#a6e3a1', stroke_width=0),
    Text('p2', x=P2X + 5, y=P2Y - 10, font_size=11, fill='#a6e3a1'),
    Text('radius', x=VX + 38, y=VY - 8, font_size=10, fill='#f9e2af'),
)

# Title
canvas.add_objects(Text('Angle', x=90, y=30, font_size=14, fill='#cdd6f4'))

# --- RightAngle indicator (right side) ---
RVX, RVY = 330, 180
RP1X, RP1Y = RVX + 80, RVY
RP2X, RP2Y = RVX, RVY - 80

canvas.add_objects(
    Line(x1=RVX, y1=RVY, x2=RP1X, y2=RP1Y, stroke='#58C4DD', stroke_width=2),
    Line(x1=RVX, y1=RVY, x2=RP2X, y2=RP2Y, stroke='#58C4DD', stroke_width=2),
)

# Right-angle square
SZ = 18
canvas.add_objects(
    Lines((RVX + SZ, RVY), (RVX + SZ, RVY - SZ), (RVX, RVY - SZ),
          stroke='#f9e2af', stroke_width=2, fill_opacity=0),
)

canvas.add_objects(
    Dot(r=4, cx=RVX, cy=RVY, fill='#f38ba8', stroke_width=0),
    Text('size', x=RVX + SZ + 4, y=RVY - SZ // 2 + 3, font_size=10, fill='#f9e2af'),
)

# Title
canvas.add_objects(Text('RightAngle', x=290, y=30, font_size=14, fill='#cdd6f4'))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'angle_params.svg')
canvas.write_frame(time=0, filename=out)
