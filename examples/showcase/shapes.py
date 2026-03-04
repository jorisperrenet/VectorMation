"""Grid showcase of special shape types."""
from vectormation.objects import *

COLS = 4
ROW_H = 280
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 3

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

COLORS = ['#58C4DD', '#83C167', '#FC6255', '#F0AC5F', '#9A72AC', '#5CD0B3']

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 80

title = Text(text='Shape Types', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

def label(name, col, row):
    return Text(text=name, x=col_x(col), y=lbl_y(row), font_size=22,
                fill='#aaa', stroke_width=0, text_anchor='middle')

# ── Row 0 ──────────────────────────────────────────────────────────

objs.append(label('AnnotationDot', 0, 0))
objs.append(AnnotationDot(r=20, cx=col_x(0), cy=obj_y(0),
                           stroke=COLORS[0], fill=COLORS[0]))

objs.append(label('ArcBetweenPoints', 1, 0))
cx1, cy1 = col_x(1), obj_y(0)
objs.append(ArcBetweenPoints(start=(cx1 - 70, cy1 + 30),
                              end=(cx1 + 70, cy1 - 30),
                              angle=60, stroke=COLORS[1], stroke_width=4))

objs.append(label('Elbow', 2, 0))
objs.append(Elbow(cx=col_x(2), cy=obj_y(0), width=60, height=60,
                   stroke=COLORS[2], stroke_width=5))

objs.append(label('AnnularSector', 3, 0))
objs.append(AnnularSector(inner_radius=40, outer_radius=80,
                           cx=col_x(3), cy=obj_y(0),
                           start_angle=20, end_angle=140,
                           fill=COLORS[3], stroke=COLORS[3]))

# ── Row 1 ──────────────────────────────────────────────────────────

objs.append(label('ArcPolygon', 0, 1))
cx0, cy0 = col_x(0), obj_y(1)
sz = 60
objs.append(ArcPolygon(
    (cx0, cy0 - sz), (cx0 + sz, cy0 + sz // 2), (cx0 - sz, cy0 + sz // 2),
    arc_angles=25, stroke=COLORS[4], fill=COLORS[4], fill_opacity=0.3))

objs.append(label('CubicBezier', 1, 1))
cx1, cy1 = col_x(1), obj_y(1)
objs.append(CubicBezier(
    p0=(cx1 - 80, cy1 + 40), p1=(cx1 - 30, cy1 - 60),
    p2=(cx1 + 30, cy1 - 60), p3=(cx1 + 80, cy1 + 40),
    stroke=COLORS[5], stroke_width=4))

objs.append(label('DashedLine', 2, 1))
cx2, cy2 = col_x(2), obj_y(1)
objs.append(DashedLine(x1=cx2 - 80, y1=cy2 + 30,
                        x2=cx2 + 80, y2=cy2 - 30,
                        dash='12,6', stroke=COLORS[0], stroke_width=4))

objs.append(label('KochSnowflake', 3, 1))
objs.append(KochSnowflake(cx=col_x(3), cy=obj_y(1), size=140, depth=3,
                           stroke=COLORS[1], fill=COLORS[1], fill_opacity=0.15))

# ── Row 2 ──────────────────────────────────────────────────────────

objs.append(label('SierpinskiTriangle', 0, 2))
objs.append(SierpinskiTriangle(cx=col_x(0), cy=obj_y(2), size=150, depth=4,
                                fill=COLORS[2], stroke=COLORS[2]))

objs.append(label('SurroundingCircle', 1, 2))
sq = Square(side=60, x=col_x(1), y=obj_y(2),
            fill=COLORS[3], fill_opacity=0.5, stroke=COLORS[3])
sc = SurroundingCircle(sq, buff=12, stroke=COLORS[4], stroke_width=3)
objs += [sq, sc]

objs.append(label('BackgroundRectangle', 2, 2))
txt = Text(text='Hello!', x=col_x(2), y=obj_y(2), font_size=32,
           fill='#fff', stroke_width=0, text_anchor='middle')
bg = BackgroundRectangle(txt, buff=10, fill='#333', fill_opacity=0.8)
objs += [bg, txt]

objs.append(label('Spiral', 3, 2))
objs.append(Spiral(cx=col_x(3), cy=obj_y(2), a=5, b=5, turns=4,
                    stroke=COLORS[5], stroke_width=2))

canvas.add_objects(*objs)

canvas.show()
