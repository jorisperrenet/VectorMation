#!/usr/bin/env python3
"""Generate annulus parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *

W, H = 400, 320
canvas = VectorMathAnim(save_dir='/tmp', width=W, height=H)
canvas.set_background(fill='#1e1e2e')

CX, CY = 200, 160
OUTER, INNER = 100, 50

# Annulus
canvas.add_objects(Annulus(inner_radius=INNER, outer_radius=OUTER, cx=CX, cy=CY,
                           fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=2.5))

# Centre dot
canvas.add_objects(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))
canvas.add_objects(Text('(cx, cy)', x=CX + 8, y=CY + 18, font_size=11, fill='#f38ba8'))

# outer_radius dimension (going right)
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=CX + OUTER, y2=CY, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=CX + OUTER - 10, y1=CY, x2=CX + OUTER, y2=CY, tip_length=6, tip_width=5, stroke='#cdd6f4', stroke_width=0),
    Text('outer_radius', x=CX + 18, y=CY - 8, font_size=12, fill='#cdd6f4'),
)

# inner_radius dimension (going up)
canvas.add_objects(
    DashedLine(x1=CX, y1=CY, x2=CX, y2=CY - INNER, dash='5,3', stroke='#a6e3a1', stroke_width=1.2),
    Arrow(x1=CX, y1=CY - INNER + 10, x2=CX, y2=CY - INNER, tip_length=6, tip_width=5, stroke='#a6e3a1', stroke_width=0),
    Text('inner_radius', x=CX + 10, y=CY - INNER//2 + 5, font_size=12, fill='#a6e3a1'),
)

# Subtitle
canvas.add_objects(Text('Ring/donut shape (even-odd fill)', x=95, y=295, font_size=11, fill='#585b70'))

out = os.path.join(os.path.dirname(__file__), '..', 'source', '_static', 'images', 'annulus_params.svg')
canvas.write_frame(time=0, filename=out)
