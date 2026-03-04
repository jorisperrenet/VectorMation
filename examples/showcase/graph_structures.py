"""2x2 animated grid showcasing graph and tree structures."""
from vectormation.objects import *

COLS = 2
ROW_H = 450
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 2
ROW_DUR = 4.0

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 30
def row_t(r): return 0.5 + r * ROW_DUR

title = Text(text='Graph Structures', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# ── (0,0) NetworkGraph ────────────────────────────────────────────────────

lbl = Text(text='NetworkGraph (spring)', x=col_x(0), y=lbl_y(0), font_size=18,
           fill='#999', stroke_width=0, text_anchor='middle')
lbl.fadein(0, 0.5)

graph = NetworkGraph(
    nodes={'s': 'S', 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 't': 'T'},
    edges=[('s', 'a', '10'), ('s', 'b', '8'), ('a', 'c', '5'), ('a', 'd', '7'),
           ('b', 'c', '3'), ('b', 'd', '6'), ('c', 't', '4'), ('d', 't', '9')],
    layout='spring', directed=True, node_r=25,
    cx=col_x(0), cy=obj_y(0) + 160,
)
a = row_t(0)
graph.fadein(a, a + 1)
graph.highlight_node('s', a + 1.5, a + 2.5, color='#83C167')
graph.highlight_node('a', a + 2.0, a + 3.0, color='#83C167')
graph.highlight_node('d', a + 2.5, a + 3.5, color='#83C167')
objs.extend([lbl, graph])

# ── (1,0) FlowChart ──────────────────────────────────────────────────────

lbl = Text(text='FlowChart', x=col_x(1), y=lbl_y(0), font_size=18,
           fill='#999', stroke_width=0, text_anchor='middle')
lbl.fadein(0, 0.5)

flow = FlowChart(
    ['Input', 'Process', 'Validate', 'Output'],
    direction='right', x=col_x(1) - 370, y=obj_y(0) + 120,
    box_width=160, box_height=50, spacing=60,
    box_color='#58C4DD', font_size=18,
)
a = row_t(0) + 0.5
flow.stagger('fadein', start=a, end=a + 1.5)
objs.extend([lbl, flow])

# ── (0,1) Tree ───────────────────────────────────────────────────────────

lbl = Text(text='Tree (BST search)', x=col_x(0), y=lbl_y(1), font_size=18,
           fill='#999', stroke_width=0, text_anchor='middle')
lbl.fadein(row_t(1) - 0.5, row_t(1))

tree = Tree(
    ('8', [
        ('3', [('1', []), ('6', [('4', []), ('7', [])])]),
        ('10', [('', []), ('14', [('13', []), ('', [])])]),
    ]),
    cx=col_x(0), cy=obj_y(1), h_spacing=80, v_spacing=90, node_r=20, font_size=16,
)
a = row_t(1)
tree.fadein(a, a + 0.8)
tree.highlight_node('8', a + 1.0, a + 2.0, color='#83C167')
tree.highlight_node('3', a + 1.5, a + 2.5, color='#83C167')
tree.highlight_node('6', a + 2.0, a + 3.0, color='#83C167')
tree.highlight_node('4', a + 2.5, a + 3.5, color='#FFFF00')
objs.extend([lbl, tree])

# ── (1,1) NetworkTree + Legend ────────────────────────────────────────────

lbl = Text(text='NetworkTree + Legend', x=col_x(1), y=lbl_y(1), font_size=18,
           fill='#999', stroke_width=0, text_anchor='middle')
lbl.fadein(row_t(1) - 0.5, row_t(1))

ntree = Tree(
    {'CEO': {'CTO': {'Dev': {}, 'QA': {}}, 'CFO': {'Acct': {}}}},
    cx=col_x(1), cy=obj_y(1) + 30, h_spacing=120, v_spacing=90,
)
a = row_t(1) + 0.5
ntree.write(a, a + 1.5)
ntree.highlight_node('CTO', start=a + 2, end=a + 3)

legend = Legend([('#58C4DD', 'Network'), ('#83C167', 'Tree'), ('#FF6B6B', 'Flow')],
               x=col_x(1) - 80, y=obj_y(1) + 320, font_size=14)
legend.fadein(a + 1.5, a + 2)
objs.extend([lbl, ntree, legend])

# ── Output ────────────────────────────────────────────────────────────────

canvas.add_objects(*objs)

total_dur = row_t(1) + ROW_DUR + 0.5

canvas.show(end=total_dur)
