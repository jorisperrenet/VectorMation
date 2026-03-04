from vectormation.objects import *

COLS = 3
ROW_H = 350
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 2

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 80

title = Text(text='Diagram Types', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

# ── Row 0, Col 0: VennDiagram ──────────────────────────────────────────────
objs.append(Text(text='VennDiagram', x=col_x(0), y=lbl_y(0), font_size=22,
                 fill='#ccc', stroke_width=0, text_anchor='middle'))
objs.append(VennDiagram(labels=['Sets', 'Logic', 'Math'],
                        x=col_x(0), y=obj_y(0) + 60, radius=90, font_size=16))

# ── Row 0, Col 1: OrgChart ─────────────────────────────────────────────────
objs.append(Text(text='OrgChart', x=col_x(1), y=lbl_y(0), font_size=22,
                 fill='#ccc', stroke_width=0, text_anchor='middle'))
org_root = ('CEO', [
    ('CTO', [('Dev', []), ('QA', [])]),
    ('CFO', [('Acct', [])]),
])
objs.append(OrgChart(root=org_root, x=col_x(1), y=obj_y(0) - 20,
                     h_spacing=110, v_spacing=70, box_width=80, box_height=30,
                     font_size=13))

# ── Row 0, Col 2: MindMap ──────────────────────────────────────────────────
objs.append(Text(text='MindMap', x=col_x(2), y=lbl_y(0), font_size=22,
                 fill='#ccc', stroke_width=0, text_anchor='middle'))
mind_root = ('Core', [
    ('Design', []),
    ('Code', []),
    ('Test', []),
    ('Deploy', []),
])
objs.append(MindMap(root=mind_root, cx=col_x(2), cy=obj_y(0) + 60,
                    radius=120, font_size=14))

# ── Row 1, Col 0: BoxPlot ──────────────────────────────────────────────────
objs.append(Text(text='BoxPlot', x=col_x(0), y=lbl_y(1), font_size=22,
                 fill='#ccc', stroke_width=0, text_anchor='middle'))
import random
random.seed(42)
data = [
    [random.gauss(50, 10) for _ in range(30)],
    [random.gauss(65, 15) for _ in range(30)],
    [random.gauss(40, 8) for _ in range(30)],
]
objs.append(BoxPlot(data_groups=data, x=col_x(0) - 200, y=obj_y(1) - 30,
                    plot_width=400, plot_height=250, box_width=35, font_size=11))

# ── Row 1, Col 1: BinaryTree ───────────────────────────────────────────────
objs.append(Text(text='BinaryTree', x=col_x(1), y=lbl_y(1), font_size=22,
                 fill='#ccc', stroke_width=0, text_anchor='middle'))
tree = ('A',
        ('B', ('D', None, None), ('E', None, None)),
        ('C', None, ('F', None, None)))
objs.append(BinaryTree(tree=tree, x=col_x(1), y=obj_y(1) - 20,
                        h_spacing=130, v_spacing=80, node_radius=20,
                        font_size=16))

# ── Row 1, Col 2: Stamp ────────────────────────────────────────────────────
objs.append(Text(text='Stamp', x=col_x(2), y=lbl_y(1), font_size=22,
                 fill='#ccc', stroke_width=0, text_anchor='middle'))
star_template = Star(n=5, outer_radius=30, inner_radius=12,
                     cx=0, cy=0, fill='#FFD700', fill_opacity=0.85,
                     stroke='#FFA500', stroke_width=2)
cx2 = col_x(2)
cy2 = obj_y(1) + 60
stamp_points = [
    (cx2 - 100, cy2 - 50),
    (cx2 + 100, cy2 - 50),
    (cx2, cy2 + 60),
    (cx2 - 60, cy2 + 30),
]
objs.append(Stamp(template=star_template, points=stamp_points))

canvas.add_objects(*objs)

canvas.show()
