#!/usr/bin/env python3
"""Generate ellipse parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 400, 300
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

CX, CY, RX, RY = 200, 145, 120, 70

# Main ellipse
canvas.add_objects(Ellipse(rx=RX, ry=RY, cx=CX, cy=CY, fill_opacity=0, stroke='#58C4DD', stroke_width=2.5))

# Centre dot
canvas.add_objects(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))
canvas.add_objects(Text('(cx, cy)', x=CX + 8, y=CY + 18, font_size=11, fill='#f38ba8'))

# rx dimension
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=CX + RX, y2=CY, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=CX + RX - 10, y1=CY, x2=CX + RX, y2=CY, tip_length=6, tip_width=5, stroke='#cdd6f4', stroke_width=0),
    Text('rx', x=CX + RX//2 - 6, y=CY - 8, font_size=14, fill='#cdd6f4'),
)

# ry dimension
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=CX, y2=CY - RY, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=CX, y1=CY - RY + 10, x2=CX, y2=CY - RY, tip_length=6, tip_width=5, stroke='#cdd6f4', stroke_width=0),
    Text('ry', x=CX + 10, y=CY - RY//2 + 5, font_size=14, fill='#cdd6f4'),
)

# cx dimension
canvas.add_objects(
    DashedLine(x1=CX, y1=250, x2=CX, y2=265, dash='3,2', stroke='#a6adc8', stroke_width=1),
    Arrow(x1=25, y1=260, x2=CX, y2=260, tip_length=8, tip_width=6, stroke='#a6adc8', stroke_width=1),
    Text('cx', x=102, y=278, font_size=12, fill='#a6adc8'),
)

# cy dimension
canvas.add_objects(
    DashedLine(x1=35, y1=CY, x2=50, y2=CY, dash='3,2', stroke='#a6adc8', stroke_width=1),
    Arrow(x1=40, y1=20, x2=40, y2=CY, tip_length=8, tip_width=6, stroke='#a6adc8', stroke_width=1),
    Text('cy', x=20, y=85, font_size=12, fill='#a6adc8'),
)

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'ellipse_params.svg')
canvas.write_frame(time=0, filename=out)
