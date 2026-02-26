#!/usr/bin/env python3
"""Generate circle parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 400, 300
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

CX, CY, R = 200, 150, 80

# Main circle
canvas.add_objects(Circle(r=R, cx=CX, cy=CY, fill_opacity=0, stroke='#58C4DD', stroke_width=2.5))

# Centre dot
canvas.add_objects(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))

# r dimension line
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=CX+R, y2=CY, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('r', x=CX + R//2 - 4, y=CY - 8, font_size=14, fill='#cdd6f4'),
)

# (cx, cy) label
canvas.add_objects(Text('(cx, cy)', x=CX + 8, y=CY + 18, font_size=11, fill='#f38ba8'))

# cx dimension
canvas.add_objects(
    DashedLine(x1=CX, y1=245, x2=CX, y2=260, dash='3,2', stroke='#a6adc8', stroke_width=1),
    Arrow(x1=30, y1=255, x2=CX, y2=255, tip_length=8, tip_width=6, stroke='#a6adc8', stroke_width=1),
    Text('cx', x=105, y=275, font_size=12, fill='#a6adc8'),
)

# cy dimension
canvas.add_objects(
    DashedLine(x1=30, y1=CY, x2=45, y2=CY, dash='3,2', stroke='#a6adc8', stroke_width=1),
    Arrow(x1=35, y1=20, x2=35, y2=CY, tip_length=8, tip_width=6, stroke='#a6adc8', stroke_width=1),
    Text('cy', x=15, y=90, font_size=12, fill='#a6adc8'),
)

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'circle_params.svg')
canvas.write_frame(time=0, filename=out)
