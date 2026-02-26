#!/usr/bin/env python3
"""Generate star parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 400, 340
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

CX, CY = 200, 160
OUTER, INNER = 110, 44
N = 5

# Faint reference circles
canvas.add_objects(
    Circle(r=OUTER, cx=CX, cy=CY, fill_opacity=0, stroke='#45475a', stroke_width=0.8, stroke_dasharray='4,3'),
    Circle(r=INNER, cx=CX, cy=CY, fill_opacity=0, stroke='#45475a', stroke_width=0.8, stroke_dasharray='4,3'),
)

# Star
canvas.add_objects(Star(n=N, outer_radius=OUTER, inner_radius=INNER, cx=CX, cy=CY,
                        fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=2.5))

# Centre dot
canvas.add_objects(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))

# outer_radius dimension (upward to top point)
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=CX, y2=CY - OUTER, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=CX, y1=CY - OUTER + 10, x2=CX, y2=CY - OUTER, tip_length=6, tip_width=5, stroke='#cdd6f4', stroke_width=0),
    Text('outer_radius', x=CX - 90, y=CY - OUTER//2, font_size=12, fill='#cdd6f4'),
)

# inner_radius dimension (to inner vertex)
import math
angle = math.radians(90 + 360 / (2 * N))  # angle to first inner vertex
ix = CX - INNER * math.cos(angle)
iy = CY - INNER * math.sin(angle)
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=ix, y2=iy, dash='5,3', stroke='#a6e3a1', stroke_width=1.2),
    Arrow(x1=ix + 5, y1=iy - 3, x2=ix, y2=iy, tip_length=6, tip_width=5, stroke='#a6e3a1', stroke_width=0),
    Text('inner_radius', x=30, y=CY - 5, font_size=12, fill='#a6e3a1'),
)

# n label
canvas.add_objects(Text('n = 5 (number of points)', x=110, y=315, font_size=13, fill='#f9e2af'))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'star_params.svg')
canvas.write_frame(time=0, filename=out)
