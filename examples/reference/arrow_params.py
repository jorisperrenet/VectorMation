"""Arrow parameter diagram."""
from vectormation.objects import *

W, H = 440, 240
v = VectorMathAnim(width=W, height=H)
v.set_background(fill='#1e1e2e')

X1, Y1, X2, Y2 = 60, 120, 340, 120
TIP_L, TIP_W = 30, 20

v.add(Arrow(x1=X1, y1=Y1, x2=X2, y2=Y2,
            tip_length=TIP_L, tip_width=TIP_W,
            stroke='#58C4DD', stroke_width=2.5))

v.add(
    Dot(r=4, cx=X1, cy=Y1, fill='#f38ba8', stroke_width=0),
    Text('(x1, y1)', x=X1 - 20, y=Y1 - 15, font_size=11, fill='#f38ba8'),
)

v.add(
    Dot(r=4, cx=X2, cy=Y2, fill='#f38ba8', stroke_width=0),
    Text('(x2, y2)', x=X2 + 5, y=Y2 - 15, font_size=11, fill='#f38ba8'),
)

tip_base_x = X2 - TIP_L
v.add(
    DashedLine(x1=tip_base_x, y1=Y1 + TIP_W//2, x2=tip_base_x, y2=Y1 + 50, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=X2, y1=Y1 + TIP_W//2, x2=X2, y2=Y1 + 50, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=tip_base_x + 3, y1=Y1 + 45, x2=X2, y2=Y1 + 45, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=X2 - 3, y1=Y1 + 45, x2=tip_base_x, y2=Y1 + 45, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Text('tip_length', x=tip_base_x - 5, y=Y1 + 65, font_size=11, fill='#cdd6f4'),
)

v.add(
    DashedLine(x1=tip_base_x, y1=Y1 - TIP_W//2, x2=X2 + 40, y2=Y1 - TIP_W//2, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=tip_base_x, y1=Y1 + TIP_W//2, x2=X2 + 40, y2=Y1 + TIP_W//2, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=X2 + 35, y1=Y1 - TIP_W//2 + 3, x2=X2 + 35, y2=Y1 + TIP_W//2, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=X2 + 35, y1=Y1 + TIP_W//2 - 3, x2=X2 + 35, y2=Y1 - TIP_W//2, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Text('tip_width', x=X2 + 42, y=Y1 + 5, font_size=11, fill='#cdd6f4'),
)

v.show(end=2)
