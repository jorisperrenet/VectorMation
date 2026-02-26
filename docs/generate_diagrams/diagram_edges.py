#!/usr/bin/env python3
"""Generate get_edge() positions diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 440, 320
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

# Reference rectangle
RX, RY, RW, RH = 120, 80, 200, 140
canvas.add_objects(Rectangle(RW, RH, x=RX, y=RY,
                             fill='#58C4DD', fill_opacity=0.1, stroke='#58C4DD', stroke_width=2))

# Edge positions with dots and labels
edges = [
    ('top_left',     RX,          RY,          RX - 55,     RY - 10),
    ('top',          RX + RW//2,  RY,          RX + RW//2 - 10, RY - 14),
    ('top_right',    RX + RW,     RY,          RX + RW + 6, RY - 10),
    ('left',         RX,          RY + RH//2,  RX - 30,     RY + RH//2 + 15),
    ('center',       RX + RW//2,  RY + RH//2,  RX + RW//2 + 8, RY + RH//2 + 15),
    ('right',        RX + RW,     RY + RH//2,  RX + RW + 6, RY + RH//2 + 15),
    ('bottom_left',  RX,          RY + RH,     RX - 70,     RY + RH + 16),
    ('bottom',       RX + RW//2,  RY + RH,     RX + RW//2 - 18, RY + RH + 18),
    ('bottom_right', RX + RW,     RY + RH,     RX + RW + 6, RY + RH + 16),
]

for name, ex, ey, lx, ly in edges:
    color = '#f38ba8' if name == 'center' else '#a6e3a1'
    canvas.add_objects(
        Dot(r=4, cx=ex, cy=ey, fill=color, stroke_width=0),
        Text(name, x=lx, y=ly, font_size=10, fill=color),
    )

# Title
canvas.add_objects(Text('get_edge() positions', x=145, y=275, font_size=14, fill='#cdd6f4'))

# Usage hint
canvas.add_objects(Text("obj.get_edge('top_right')  →  (x, y)", x=90, y=300, font_size=11, fill='#585b70'))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'edges.svg')
canvas.write_frame(time=0, filename=out)
