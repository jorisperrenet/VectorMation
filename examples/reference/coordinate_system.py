"""Canvas coordinate system showing directions and origin."""
from vectormation.objects import *

W, H = 520, 360
v = VectorMathAnim(width=W, height=H)
v.set_background(fill='#1e1e2e')

# Canvas border
v.add(Rectangle(480, 300, x=20, y=30, fill_opacity=0, stroke='#45475a', stroke_width=1))

# Origin labels
v.add(
    Text('(0, 0)', x=24, y=50, font_size=10, fill='#585b70'),
    Text('(1920, 0)', x=435, y=50, font_size=10, fill='#585b70'),
    Text('(0, 1080)', x=24, y=325, font_size=10, fill='#585b70'),
    Text('(1920, 1080)', x=420, y=325, font_size=10, fill='#585b70'),
)

# Centre point (ORIGIN)
CX, CY = 260, 180
v.add(Dot(r=5, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))
v.add(Text('ORIGIN (960, 540)', x=CX + 10, y=CY + 16, font_size=11, fill='#f38ba8'))

# Direction arrows from centre
ARROW_LEN = 65

v.add(
    Arrow(x1=CX, y1=CY - 10, x2=CX, y2=CY - ARROW_LEN, tip_length=8, tip_width=6,
          stroke='#89b4fa', stroke_width=1.8),
    Text('UP', x=CX - 20, y=CY - ARROW_LEN - 10, font_size=11, fill='#89b4fa'),
)

v.add(
    Arrow(x1=CX, y1=CY + 10, x2=CX, y2=CY + ARROW_LEN, tip_length=8, tip_width=6,
          stroke='#89b4fa', stroke_width=1.8),
    Text('DOWN', x=CX - 22, y=CY + ARROW_LEN + 16, font_size=11, fill='#89b4fa'),
)

v.add(
    Arrow(x1=CX - 10, y1=CY, x2=CX - ARROW_LEN, y2=CY, tip_length=8, tip_width=6,
          stroke='#89b4fa', stroke_width=1.8),
    Text('LEFT', x=CX - ARROW_LEN - 35, y=CY + 5, font_size=11, fill='#89b4fa'),
)

v.add(
    Arrow(x1=CX + 10, y1=CY, x2=CX + ARROW_LEN, y2=CY, tip_length=8, tip_width=6,
          stroke='#89b4fa', stroke_width=1.8),
    Text('RIGHT', x=CX + ARROW_LEN + 8, y=CY + 5, font_size=11, fill='#89b4fa'),
)

v.add(
    Text('Canvas: 1920 x 1080', x=185, y=20, font_size=12, fill='#cdd6f4'),
    Text('UNIT = 135 px', x=215, y=350, font_size=11, fill='#585b70'),
    Text('Y increases downward', x=355, y=180, font_size=10, fill='#f9e2af'),
)

v.show(end=2)
