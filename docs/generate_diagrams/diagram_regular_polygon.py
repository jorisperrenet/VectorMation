#!/usr/bin/env python3
"""Generate regular polygon parameter diagram."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 400, 340
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

CX, CY = 200, 155
RADIUS = 100
N = 6

# Circumscribed circle (faint)
canvas.add_objects(
    Circle(r=RADIUS, cx=CX, cy=CY, fill_opacity=0, stroke='#45475a', stroke_width=0.8, stroke_dasharray='4,3'),
)

# Regular polygon
canvas.add_objects(RegularPolygon(N, radius=RADIUS, cx=CX, cy=CY,
                                  fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=2.5))

# Centre dot
canvas.add_objects(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))

# Radius dimension (to top vertex)
top_x = CX + RADIUS * math.cos(math.radians(90))
top_y = CY - RADIUS * math.sin(math.radians(90))
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=top_x, y2=top_y, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('radius', x=CX - 55, y=CY - RADIUS // 2 + 3, font_size=12, fill='#cdd6f4'),
)

# Angle arc indicator
canvas.add_objects(
    Arc(cx=CX, cy=CY, r=30, start_angle=0, end_angle=90,
        fill_opacity=0, stroke='#a6e3a1', stroke_width=1.2),
    Text('angle', x=CX + 32, y=CY - 18, font_size=11, fill='#a6e3a1'),
)

# n label
canvas.add_objects(Text('n = 6 (number of sides)', x=105, y=310, font_size=13, fill='#f9e2af'))

# Vertex dots
for i in range(N):
    a = math.radians(90 + i * 360 / N)
    vx = CX + RADIUS * math.cos(a)
    vy = CY - RADIUS * math.sin(a)
    canvas.add_objects(Dot(r=3, cx=vx, cy=vy, fill='#f9e2af', stroke_width=0))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'regular_polygon_params.svg')
canvas.write_frame(time=0, filename=out)
