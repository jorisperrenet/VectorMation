"""In-Order Tree Traversal — visiting every node of a balanced BST in sorted order.

Animates in-order traversal on a 15-node balanced binary tree (4 levels).
Each node is highlighted yellow when visited and turns green once done.
A sequence bar at the bottom fills in the traversal order as nodes are visited.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/tree_traversal')
canvas.set_background()

# -- Parameters ---------------------------------------------------------------
T = 14.0

# Tree values (balanced BST, level-order)
TREE_VALUES = [8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15]

# In-order traversal visits nodes in sorted order: 1, 2, 3, ..., 15
INORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

# Colors
COLOR_UNVISITED = '#4A90D9'  # blue
COLOR_CURRENT   = '#F5C542'  # yellow
COLOR_VISITED   = '#5EC16A'  # green
COLOR_TEXT      = '#FFFFFF'
COLOR_EDGE      = '#555555'

# Node size
NODE_R = 30
FONT_SIZE = 22

# Level positions
LEVEL_Y = [180, 320, 460, 600]
LEVEL_SPREAD = [0, 400, 200, 100]  # x-spread from parent center

# -- Compute node positions ---------------------------------------------------
# Index in TREE_VALUES corresponds to level-order index (0-based).
# Level 0: index 0               -> 1 node
# Level 1: indices 1-2           -> 2 nodes
# Level 2: indices 3-6           -> 4 nodes
# Level 3: indices 7-14          -> 8 nodes

node_positions = {}  # index -> (x, y)

# Root
node_positions[0] = (960, LEVEL_Y[0])

# For each subsequent level, children are at parent_x +/- spread
for level in range(1, 4):
    spread = LEVEL_SPREAD[level]
    for i in range(2 ** level):
        node_idx = 2 ** level - 1 + i
        parent_idx = (node_idx - 1) // 2
        parent_x, _ = node_positions[parent_idx]
        # Left child: parent - spread, Right child: parent + spread
        if node_idx % 2 == 1:  # left child (odd index)
            x = parent_x - spread
        else:  # right child (even index)
            x = parent_x + spread
        node_positions[node_idx] = (x, LEVEL_Y[level])

# -- Build value-to-index mapping ---------------------------------------------
value_to_idx = {}
for idx, val in enumerate(TREE_VALUES):
    value_to_idx[val] = idx

# -- Create edges (draw first so they appear behind nodes) --------------------
edges = []
for idx in range(1, 15):
    parent_idx = (idx - 1) // 2
    px, py = node_positions[parent_idx]
    cx, cy = node_positions[idx]
    edge = Line(
        x1=px, y1=py + NODE_R, x2=cx, y2=cy - NODE_R,
        stroke=COLOR_EDGE, stroke_width=2, creation=0,
    )
    edge.fadein(0.2, 0.8)
    edges.append(edge)

# -- Create nodes and labels --------------------------------------------------
nodes = []      # indexed by level-order index
node_labels = []

for idx in range(15):
    x, y = node_positions[idx]
    val = TREE_VALUES[idx]

    node = Circle(
        r=NODE_R, cx=x, cy=y,
        fill=COLOR_UNVISITED, stroke=COLOR_TEXT, stroke_width=2,
        creation=0,
    )
    node.fadein(0.2, 0.8)
    nodes.append(node)

    label = Text(
        text=str(val),
        x=x, y=y + FONT_SIZE * 0.35,
        font_size=FONT_SIZE, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
        creation=0,
    )
    label.fadein(0.3, 0.9)
    node_labels.append(label)

# -- Title --------------------------------------------------------------------
title = Text(
    text='In-Order Tree Traversal', x=960, y=60,
    font_size=48, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
title.fadein(0, 0.7)

subtitle = Text(
    text='Left  ->  Root  ->  Right', x=960, y=110,
    font_size=24, fill='#AAAAAA', stroke_width=0, text_anchor='middle',
    creation=0,
)
subtitle.fadein(0.1, 0.8)

# -- Current node label -------------------------------------------------------
current_label = Text(
    text='', x=960, y=700,
    font_size=28, fill=COLOR_CURRENT, stroke_width=0, text_anchor='middle',
    creation=0,
)
current_label.fadein(1.0, 1.3)

# -- Sequence bar at the bottom -----------------------------------------------
# 15 small boxes that fill in with green as each node is visited
SEQ_Y = 800
SEQ_CELL_SIZE = 50
SEQ_GAP = 6
SEQ_TOTAL_W = 15 * SEQ_CELL_SIZE + 14 * SEQ_GAP
SEQ_LEFT = (1920 - SEQ_TOTAL_W) / 2

seq_label = Text(
    text='Traversal Order:', x=960, y=SEQ_Y - 30,
    font_size=22, fill='#AAAAAA', stroke_width=0, text_anchor='middle',
    creation=0,
)
seq_label.fadein(0.5, 1.0)

seq_cells = []
seq_value_labels = []

for i in range(15):
    sx = SEQ_LEFT + i * (SEQ_CELL_SIZE + SEQ_GAP)
    sy = SEQ_Y

    cell = Rectangle(
        width=SEQ_CELL_SIZE, height=SEQ_CELL_SIZE,
        x=sx, y=sy,
        fill='#2A2A3E', fill_opacity=0.6,
        stroke='#555577', stroke_width=1.5,
        rx=4, ry=4,
        creation=0,
    )
    cell.fadein(0.4, 0.9)
    seq_cells.append(cell)

    # Value label (initially empty, filled in during traversal)
    val_label = Text(
        text='',
        x=sx + SEQ_CELL_SIZE / 2, y=sy + SEQ_CELL_SIZE / 2 + 5,
        font_size=18, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
        creation=0,
    )
    seq_value_labels.append(val_label)

# Position index labels below seq cells
seq_index_labels = []
for i in range(15):
    sx = SEQ_LEFT + i * (SEQ_CELL_SIZE + SEQ_GAP)
    idx_label = Text(
        text=str(i + 1),
        x=sx + SEQ_CELL_SIZE / 2, y=SEQ_Y + SEQ_CELL_SIZE + 16,
        font_size=12, fill='#666666', stroke_width=0, text_anchor='middle',
        creation=0,
    )
    idx_label.fadein(0.5, 1.0)
    seq_index_labels.append(idx_label)

# -- Animate in-order traversal -----------------------------------------------
TRAVERSE_START = 1.0
TRAVERSE_END   = 12.0
traverse_duration = TRAVERSE_END - TRAVERSE_START
step_dur = traverse_duration / 15  # ~0.73s per node

for visit_idx, value in enumerate(INORDER):
    node_idx = value_to_idx[value]
    t_start = TRAVERSE_START + visit_idx * step_dur
    t_highlight = t_start + 0.05
    t_visited = t_start + step_dur * 0.7
    t_end = t_start + step_dur

    # Highlight current node yellow
    nodes[node_idx].set_fill(color=COLOR_CURRENT, start=t_highlight, end=t_highlight + 0.15)
    nodes[node_idx].set_stroke(color=COLOR_CURRENT, start=t_highlight, end=t_highlight + 0.15)

    # Pulse the current node
    nodes[node_idx].pulsate(start=t_highlight, end=t_visited, scale_factor=1.15, n_pulses=1)

    # Update current node label
    current_label.text.set_onward(t_start, f'Visiting node: {value}')

    # Mark as visited (green) after the pulse
    nodes[node_idx].set_fill(color=COLOR_VISITED, start=t_visited, end=t_visited + 0.15)
    nodes[node_idx].set_stroke(color=COLOR_VISITED, start=t_visited, end=t_visited + 0.15)

    # Also color the edge leading to this node green (if not root)
    if node_idx > 0:
        edge_idx = node_idx - 1  # edges list is indexed by child node index - 1
        edges[edge_idx].set_stroke(color=COLOR_VISITED, start=t_visited, end=t_visited + 0.15)

    # Fill in the sequence bar cell
    seq_cells[visit_idx].set_fill(color=COLOR_VISITED, start=t_visited, end=t_visited + 0.15)
    seq_cells[visit_idx].set_stroke(color=COLOR_VISITED, start=t_visited, end=t_visited + 0.15)
    seq_value_labels[visit_idx].text.set_onward(t_visited, str(value))
    seq_value_labels[visit_idx].set_opacity(1.0, start=t_visited, end=t_visited + 0.2)

# -- Final state (12-14s) ----------------------------------------------------
FINAL_START = 12.0

current_label.text.set_onward(FINAL_START, '')

complete_label = Text(
    text='Traversal Complete!', x=960, y=700,
    font_size=44, fill=COLOR_VISITED, stroke_width=0, text_anchor='middle',
    creation=FINAL_START,
)
complete_label.fadein(FINAL_START, FINAL_START + 0.5)

# Show the full in-order sequence as text
sequence_text = Text(
    text='In-order: ' + ', '.join(str(v) for v in INORDER),
    x=960, y=750,
    font_size=24, fill='#CCCCCC', stroke_width=0, text_anchor='middle',
    creation=FINAL_START,
)
sequence_text.fadein(FINAL_START + 0.2, FINAL_START + 0.7)

# Pulse all visited nodes gently
for idx in range(15):
    nodes[idx].pulsate(start=FINAL_START, end=T, scale_factor=1.06, n_pulses=2)

# -- Legend -------------------------------------------------------------------
LEGEND_Y = 930
LEGEND_X_START = 560
LEGEND_SPACING = 280
LEGEND_SWATCH = 16

legend_items = [
    (COLOR_UNVISITED, 'Unvisited'),
    (COLOR_CURRENT, 'Current'),
    (COLOR_VISITED, 'Visited'),
]

legend_objects = []
for i, (color, label_text) in enumerate(legend_items):
    lx = LEGEND_X_START + i * LEGEND_SPACING
    swatch = Circle(
        r=LEGEND_SWATCH / 2, cx=lx, cy=LEGEND_Y,
        fill=color, stroke=color, stroke_width=1,
        creation=0,
    )
    swatch.fadein(0.5, 1.0)
    legend_objects.append(swatch)

    lbl = Text(
        text=label_text,
        x=lx + LEGEND_SWATCH, y=LEGEND_Y + 5,
        font_size=18, fill=color, stroke_width=0, text_anchor='start',
        creation=0,
    )
    lbl.fadein(0.5, 1.0)
    legend_objects.append(lbl)

# -- Add everything to canvas -------------------------------------------------
canvas.add(title, subtitle, current_label, complete_label, sequence_text)
canvas.add(seq_label)
for edge in edges:
    canvas.add(edge)
for node in nodes:
    canvas.add(node)
for label in node_labels:
    canvas.add(label)
for cell in seq_cells:
    canvas.add(cell)
for label in seq_value_labels:
    canvas.add(label)
for label in seq_index_labels:
    canvas.add(label)
for obj in legend_objects:
    canvas.add(obj)

canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
