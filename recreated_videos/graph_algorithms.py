"""Graph Algorithm Visualization — BFS traversal and shortest path on a weighted graph.

Builds a network of 8 labeled nodes with weighted edges, then animates a BFS
traversal from node A to node H.  Visited nodes change color in sequence.
At the end, the shortest path (A -> C -> F -> H) is highlighted in green.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/graph_algorithms')
canvas.set_background()

# -- Parameters ---------------------------------------------------------------
T = 12.0

# Colors
COLOR_DEFAULT    = '#4A90D9'  # blue — unvisited node
COLOR_CURRENT    = '#F5C542'  # yellow — currently visiting
COLOR_VISITED    = '#E07040'  # orange — already visited
COLOR_PATH       = '#5EC16A'  # green — shortest path
COLOR_EDGE       = '#555555'  # grey — default edge
COLOR_EDGE_VISIT = '#F5C542'  # yellow — edge being traversed
COLOR_EDGE_PATH  = '#5EC16A'  # green — shortest path edge
COLOR_TEXT       = '#FFFFFF'
COLOR_WEIGHT     = '#AAAAAA'
COLOR_QUEUE      = '#9B72AC'  # purple — queue display

NODE_R = 34
FONT_SIZE = 22

# -- Graph definition ---------------------------------------------------------
# Nodes: id -> label
node_labels = {
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D',
    'E': 'E', 'F': 'F', 'G': 'G', 'H': 'H',
}

# Manual positions for a clear, non-overlapping layout
# Arranged roughly in 3 columns across the canvas
node_positions = {
    'A': (340, 400),
    'B': (340, 680),
    'C': (660, 280),
    'D': (660, 540),
    'E': (660, 760),
    'F': (1020, 400),
    'G': (1020, 680),
    'H': (1400, 540),
}

# Edges: (from, to, weight)
edge_defs = [
    ('A', 'B', 4),
    ('A', 'C', 2),
    ('A', 'D', 5),
    ('B', 'E', 3),
    ('C', 'D', 1),
    ('C', 'F', 3),
    ('D', 'F', 2),
    ('D', 'G', 6),
    ('E', 'G', 2),
    ('F', 'H', 4),
    ('G', 'H', 3),
]

# -- BFS traversal order (from A) --------------------------------------------
# BFS visits layer by layer: A -> B, C, D -> E, F, G -> H
bfs_order = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# Parent map (the edge used to discover each node in BFS)
bfs_parent = {
    'B': 'A', 'C': 'A', 'D': 'A',
    'E': 'B', 'F': 'C', 'G': 'D',
    'H': 'F',
}

# Shortest path from A to H (by BFS in unweighted, but we show weights for flavor)
shortest_path = ['A', 'C', 'F', 'H']

# -- Title --------------------------------------------------------------------
title = Text(
    text='BFS Graph Traversal', x=960, y=70,
    font_size=48, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
title.fadein(0, 0.6)

subtitle = Text(
    text='Breadth-First Search from A to H', x=960, y=120,
    font_size=24, fill='#AAAAAA', stroke_width=0, text_anchor='middle',
    creation=0,
)
subtitle.fadein(0.1, 0.7)

# -- Create edges (lines with weight labels) ----------------------------------
edge_lines = {}   # (a, b) -> Line object
edge_weights = {} # (a, b) -> Text object

for a, b, w in edge_defs:
    ax, ay = node_positions[a]
    bx, by = node_positions[b]

    line = Line(
        x1=ax, y1=ay, x2=bx, y2=by,
        stroke=COLOR_EDGE, stroke_width=2.5, creation=0,
    )
    line.fadein(0.2, 0.7)
    edge_lines[(a, b)] = line

    # Weight label at midpoint, offset perpendicular to the edge
    mx, my = (ax + bx) / 2, (ay + by) / 2
    # Simple perpendicular offset
    dx, dy = bx - ax, by - ay
    length = (dx ** 2 + dy ** 2) ** 0.5
    if length > 0:
        px, py = -dy / length * 16, dx / length * 16
    else:
        px, py = 0, -16

    weight_lbl = Text(
        text=str(w), x=mx + px, y=my + py + 6,
        font_size=16, fill=COLOR_WEIGHT, stroke_width=0, text_anchor='middle',
        creation=0,
    )
    weight_lbl.fadein(0.3, 0.8)
    edge_weights[(a, b)] = weight_lbl

# -- Create nodes (circles with labels) ---------------------------------------
node_circles = {}
node_text_objs = {}

for nid, label in node_labels.items():
    nx, ny = node_positions[nid]

    circle = Circle(
        r=NODE_R, cx=nx, cy=ny,
        fill=COLOR_DEFAULT, fill_opacity=0.9,
        stroke=COLOR_TEXT, stroke_width=2.5,
        creation=0, z=1,
    )
    circle.fadein(0.2, 0.7)
    node_circles[nid] = circle

    lbl = Text(
        text=label, x=nx, y=ny + FONT_SIZE * 0.35,
        font_size=FONT_SIZE, fill=COLOR_TEXT, stroke_width=0,
        text_anchor='middle', creation=0, z=2,
    )
    lbl.fadein(0.3, 0.8)
    node_text_objs[nid] = lbl

# -- Status label (shows current action) --------------------------------------
status_label = Text(
    text='', x=960, y=180,
    font_size=26, fill=COLOR_CURRENT, stroke_width=0, text_anchor='middle',
    creation=0,
)

# -- Queue display at the bottom ----------------------------------------------
QUEUE_Y = 920
queue_title = Text(
    text='Queue:', x=200, y=QUEUE_Y + 6,
    font_size=22, fill=COLOR_QUEUE, stroke_width=0, text_anchor='end',
    creation=0,
)
queue_title.fadein(0.8, 1.2)

queue_display = Text(
    text='', x=220, y=QUEUE_Y + 6,
    font_size=22, fill=COLOR_QUEUE, stroke_width=0, text_anchor='start',
    creation=0,
)
queue_display.fadein(0.8, 1.2)

# -- Animate BFS traversal ---------------------------------------------------
BFS_START = 1.0
BFS_END = 8.5
bfs_duration = BFS_END - BFS_START
step_dur = bfs_duration / len(bfs_order)

# Simulate the queue state for display
queue_state = ['A']

for visit_idx, nid in enumerate(bfs_order):
    t_start = BFS_START + visit_idx * step_dur
    t_arrive = t_start + 0.1
    t_visit = t_start + step_dur * 0.35
    t_done = t_start + step_dur * 0.75
    t_end = t_start + step_dur

    # Show queue state
    queue_display.text.set_onward(t_start, '[ ' + ', '.join(queue_state) + ' ]')

    # Highlight the edge used to reach this node (if not root)
    if nid in bfs_parent:
        parent = bfs_parent[nid]
        edge_key = (parent, nid) if (parent, nid) in edge_lines else (nid, parent)
        if edge_key in edge_lines:
            edge_lines[edge_key].set_stroke(
                color=COLOR_EDGE_VISIT, start=t_arrive, end=t_arrive + 0.2,
            )

    # Highlight current node yellow
    node_circles[nid].set_fill(color=COLOR_CURRENT, start=t_arrive, end=t_arrive + 0.15)
    node_circles[nid].set_stroke(color=COLOR_CURRENT, start=t_arrive, end=t_arrive + 0.15)
    node_circles[nid].pulsate(start=t_arrive, end=t_visit, scale_factor=1.15, n_pulses=1)

    # Update status
    if nid == 'A':
        status_label.text.set_onward(t_start, f'Start BFS at node {nid}')
    else:
        parent = bfs_parent[nid]
        status_label.text.set_onward(t_start, f'Visit {nid}  (discovered from {parent})')

    # Dequeue: remove current from front, add unvisited neighbors
    if nid in queue_state:
        queue_state.remove(nid)

    # Add neighbors that haven't been visited yet
    visited_set = set(bfs_order[:visit_idx + 1])
    queued_set = set(queue_state)
    for a, b, w in edge_defs:
        neighbor = None
        if a == nid and b not in visited_set and b not in queued_set:
            neighbor = b
        elif b == nid and a not in visited_set and a not in queued_set:
            neighbor = a
        if neighbor:
            queue_state.append(neighbor)

    # Mark node as visited (orange)
    node_circles[nid].set_fill(color=COLOR_VISITED, start=t_done, end=t_done + 0.15)
    node_circles[nid].set_stroke(color=COLOR_VISITED, start=t_done, end=t_done + 0.15)

    # Update queue display after dequeue + enqueue
    queue_display.text.set_onward(t_visit, '[ ' + ', '.join(queue_state) + ' ]' if queue_state else '[ empty ]')

# -- Transition to shortest path (8.5s - 9.0s) --------------------------------
status_label.text.set_onward(BFS_END, 'BFS complete! Highlighting shortest path A -> H ...')
status_label.set_fill(color=COLOR_PATH, start=BFS_END)
queue_display.text.set_onward(BFS_END, '[ empty ]')

# -- Highlight shortest path (9.0s - 11.0s) -----------------------------------
PATH_START = 9.0
PATH_END = 11.0
path_step_dur = (PATH_END - PATH_START) / (len(shortest_path))

for i, nid in enumerate(shortest_path):
    t = PATH_START + i * path_step_dur
    t_arrive = t + 0.1

    # Highlight path node green
    node_circles[nid].set_fill(color=COLOR_PATH, start=t_arrive, end=t_arrive + 0.15)
    node_circles[nid].set_stroke(color=COLOR_PATH, start=t_arrive, end=t_arrive + 0.15)
    node_circles[nid].pulsate(start=t_arrive, end=t_arrive + path_step_dur * 0.6, scale_factor=1.12, n_pulses=1)

    # Highlight the edge on the path
    if i > 0:
        prev = shortest_path[i - 1]
        edge_key = (prev, nid) if (prev, nid) in edge_lines else (nid, prev)
        if edge_key in edge_lines:
            edge_lines[edge_key].set_stroke(
                color=COLOR_EDGE_PATH, width=4.5, start=t, end=t + 0.2,
            )

# -- Final state (11.0s - 12.0s) ---------------------------------------------
FINAL_START = 11.0

status_label.text.set_onward(FINAL_START, '')

path_text = ' -> '.join(shortest_path)
result_label = Text(
    text=f'Shortest Path: {path_text}', x=960, y=180,
    font_size=40, fill=COLOR_PATH, stroke_width=0, text_anchor='middle',
    creation=FINAL_START, z=3,
)
result_label.fadein(FINAL_START, FINAL_START + 0.4)

# Compute total weight along shortest path
path_weight = 0
for i in range(len(shortest_path) - 1):
    a, b = shortest_path[i], shortest_path[i + 1]
    for ea, eb, w in edge_defs:
        if (ea == a and eb == b) or (ea == b and eb == a):
            path_weight += w
            break

weight_label = Text(
    text=f'Total weight: {path_weight}', x=960, y=230,
    font_size=28, fill='#CCCCCC', stroke_width=0, text_anchor='middle',
    creation=FINAL_START, z=3,
)
weight_label.fadein(FINAL_START + 0.2, FINAL_START + 0.6)

# Pulse the path nodes gently in the final phase
for nid in shortest_path:
    node_circles[nid].pulsate(start=FINAL_START, end=T, scale_factor=1.06, n_pulses=2)

# -- Legend -------------------------------------------------------------------
LEGEND_Y = 970
LEGEND_X_START = 480
LEGEND_SPACING = 260
LEGEND_SWATCH = 16

legend_items = [
    (COLOR_DEFAULT, 'Unvisited'),
    (COLOR_CURRENT, 'Current'),
    (COLOR_VISITED, 'Visited'),
    (COLOR_PATH, 'Shortest Path'),
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
canvas.add(title, subtitle, status_label)
canvas.add(queue_title, queue_display)
canvas.add(result_label, weight_label)

for line in edge_lines.values():
    canvas.add(line)
for wlbl in edge_weights.values():
    canvas.add(wlbl)
for circle in node_circles.values():
    canvas.add(circle)
for lbl in node_text_objs.values():
    canvas.add(lbl)
for obj in legend_objects:
    canvas.add(obj)

if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
