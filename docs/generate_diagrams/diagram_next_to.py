#!/usr/bin/env python3
"""Generate next_to positioning diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 440, 320
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

# Central reference object
CX, CY = 220, 155
ref = Rectangle(70, 50, x=CX - 35, y=CY - 25,
                fill='#58C4DD', fill_opacity=0.2, stroke='#58C4DD', stroke_width=2)
canvas.add_objects(ref)
canvas.add_objects(Text('target', x=CX - 19, y=CY + 5, font_size=11, fill='#58C4DD'))

# Positioned objects in each direction
BUFF = 12
positions = [
    ('right', CX + 35 + BUFF,     CY,     '#a6e3a1'),
    ('left',  CX - 35 - BUFF - 50, CY,    '#f38ba8'),
    ('up',    CX,                  CY - 25 - BUFF - 25, '#89b4fa'),
    ('down',  CX,                  CY + 25 + BUFF,      '#f9e2af'),
]

for direction, px, py, color in positions:
    rx, ry = px - 25, py - 12
    if direction == 'left':
        rx = px
    canvas.add_objects(
        Rectangle(50, 25, x=rx, y=ry,
                  fill=color, fill_opacity=0.2, stroke=color, stroke_width=1.5),
    )

    # Direction label
    label_offsets = {
        'right': (px + 30, py + 4),
        'left':  (px - 40, py + 4),
        'up':    (px + 30, py),
        'down':  (px + 30, py + 10),
    }
    lx, ly = label_offsets[direction]
    canvas.add_objects(Text(f"'{direction}'", x=lx, y=ly, font_size=10, fill=color))

# Buff annotation (between target and right)
canvas.add_objects(
    DashedLine(x1=CX + 35, y1=CY + 30, x2=CX + 35, y2=CY + 45, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=CX + 35 + BUFF, y1=CY + 30, x2=CX + 35 + BUFF, y2=CY + 45, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Text('buff', x=CX + 37, y=CY + 55, font_size=10, fill='#cdd6f4'),
)

# Title
canvas.add_objects(Text("next_to(target, direction, buff)", x=100, y=270, font_size=13, fill='#cdd6f4'))

# Usage
canvas.add_objects(Text("obj.next_to(target, 'right', buff=12)", x=95, y=295, font_size=11, fill='#585b70'))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'next_to.svg')
canvas.write_frame(time=0, filename=out)
