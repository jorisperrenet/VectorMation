"""Neural Network Forward Pass — feed-forward propagation visualization.

Animates a 3-layer neural network (3-4-2) with forward propagation.
Data flows from left to right: input nodes activate, connections light up
in sequence, hidden nodes activate, then output nodes show classification.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/neural_network')
canvas.set_background()

# -- Parameters ---------------------------------------------------------------
T = 12.0

# Colors
COLOR_INACTIVE    = '#2c3e50'
COLOR_STROKE      = '#FFFFFF'
COLOR_ACTIVE      = '#58C4DD'   # cyan glow
COLOR_CONN_OFF    = '#444444'
COLOR_CONN_ON     = '#58C4DD'
COLOR_OUTPUT_POS  = '#5EC16A'   # green
COLOR_OUTPUT_NEG  = '#E84D4D'   # red
COLOR_TEXT        = '#FFFFFF'
COLOR_LABEL       = '#AAAAAA'

# Node layout
NODE_R = 30
FONT_SIZE = 20

INPUT_X  = 300
HIDDEN_X = 760
OUTPUT_X = 1220

INPUT_YS  = [340, 440, 540]
HIDDEN_YS = [290, 390, 490, 590]
OUTPUT_YS = [390, 490]

INPUT_VALUES  = [0.8, 0.3, 0.6]
OUTPUT_VALUES = [0.87, 0.13]

# -- Title --------------------------------------------------------------------
title = Text(
    text='Neural Network Forward Pass', x=960, y=70,
    font_size=48, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
    creation=0,
)
title.fadein(0, 1.0)

subtitle = Text(
    text='3-4-2 Feed-Forward Network', x=960, y=120,
    font_size=24, fill=COLOR_LABEL, stroke_width=0, text_anchor='middle',
    creation=0,
)
subtitle.fadein(0.2, 1.0)

# -- Layer labels -------------------------------------------------------------
input_label = Text(
    text='Input Layer', x=INPUT_X, y=240,
    font_size=26, fill=COLOR_LABEL, stroke_width=0, text_anchor='middle',
    creation=0,
)
input_label.fadein(0.3, 1.0)

hidden_label = Text(
    text='Hidden Layer', x=HIDDEN_X, y=190,
    font_size=26, fill=COLOR_LABEL, stroke_width=0, text_anchor='middle',
    creation=0,
)
hidden_label.fadein(0.3, 1.0)

output_label = Text(
    text='Output Layer', x=OUTPUT_X, y=290,
    font_size=26, fill=COLOR_LABEL, stroke_width=0, text_anchor='middle',
    creation=0,
)
output_label.fadein(0.3, 1.0)

# -- Create connections (drawn first so nodes appear on top) ------------------
# Input -> Hidden connections
ih_connections = []
for i, iy in enumerate(INPUT_YS):
    for j, hy in enumerate(HIDDEN_YS):
        conn = Line(
            x1=INPUT_X + NODE_R, y1=iy,
            x2=HIDDEN_X - NODE_R, y2=hy,
            stroke=COLOR_CONN_OFF, stroke_width=1.5, stroke_opacity=0.3,
            creation=0,
        )
        conn.fadein(0.3, 0.9)
        ih_connections.append((i, j, conn))

# Hidden -> Output connections
ho_connections = []
for j, hy in enumerate(HIDDEN_YS):
    for k, oy in enumerate(OUTPUT_YS):
        conn = Line(
            x1=HIDDEN_X + NODE_R, y1=hy,
            x2=OUTPUT_X - NODE_R, y2=oy,
            stroke=COLOR_CONN_OFF, stroke_width=1.5, stroke_opacity=0.3,
            creation=0,
        )
        conn.fadein(0.3, 0.9)
        ho_connections.append((j, k, conn))

# -- Create nodes -------------------------------------------------------------
# Input nodes
input_nodes = []
input_value_labels = []
for i, iy in enumerate(INPUT_YS):
    node = Circle(
        r=NODE_R, cx=INPUT_X, cy=iy,
        fill=COLOR_INACTIVE, stroke=COLOR_STROKE, stroke_width=2,
        creation=0,
    )
    node.fadein(0.2, 0.8)
    input_nodes.append(node)

    val_label = Text(
        text='', x=INPUT_X, y=iy + FONT_SIZE * 0.35,
        font_size=FONT_SIZE, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
        creation=0,
    )
    input_value_labels.append(val_label)

# Hidden nodes
hidden_nodes = []
hidden_value_labels = []
for j, hy in enumerate(HIDDEN_YS):
    node = Circle(
        r=NODE_R, cx=HIDDEN_X, cy=hy,
        fill=COLOR_INACTIVE, stroke=COLOR_STROKE, stroke_width=2,
        creation=0,
    )
    node.fadein(0.2, 0.8)
    hidden_nodes.append(node)

    val_label = Text(
        text='', x=HIDDEN_X, y=hy + FONT_SIZE * 0.35,
        font_size=FONT_SIZE, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
        creation=0,
    )
    hidden_value_labels.append(val_label)

# Output nodes
output_nodes = []
output_value_labels = []
for k, oy in enumerate(OUTPUT_YS):
    node = Circle(
        r=NODE_R, cx=OUTPUT_X, cy=oy,
        fill=COLOR_INACTIVE, stroke=COLOR_STROKE, stroke_width=2,
        creation=0,
    )
    node.fadein(0.2, 0.8)
    output_nodes.append(node)

    val_label = Text(
        text='', x=OUTPUT_X, y=oy + FONT_SIZE * 0.35,
        font_size=FONT_SIZE, fill=COLOR_TEXT, stroke_width=0, text_anchor='middle',
        creation=0,
    )
    output_value_labels.append(val_label)

# -- Status label (bottom) ---------------------------------------------------
status_label = Text(
    text='', x=960, y=750,
    font_size=28, fill=COLOR_LABEL, stroke_width=0, text_anchor='middle',
    creation=0,
)

# -- Classification label (appears at end) ------------------------------------
class_label = Text(
    text='', x=960, y=830,
    font_size=40, fill=COLOR_OUTPUT_POS, stroke_width=0, text_anchor='middle',
    creation=0,
)

# == Animation Timeline =======================================================

# -- Phase 1 (1-2s): Input nodes activate with values ------------------------
for i, val in enumerate(INPUT_VALUES):
    t_act = 1.0 + i * 0.3  # stagger slightly
    input_nodes[i].set_fill(color=COLOR_ACTIVE, start=t_act, end=t_act + 0.2)
    input_nodes[i].set_stroke(color=COLOR_ACTIVE, start=t_act, end=t_act + 0.2)
    input_nodes[i].pulsate(start=t_act, end=t_act + 0.5, scale_factor=1.15, n_pulses=1)
    input_value_labels[i].text.set_onward(t_act, str(val))
    input_value_labels[i].set_opacity(1.0, start=t_act, end=t_act + 0.2)

status_label.text.set_onward(1.0, 'Feeding input values...')
status_label.set_opacity(1.0, start=1.0, end=1.3)

# -- Phase 2 (2-5s): Input -> Hidden propagation -----------------------------
# Light up connections from each input node to each hidden node sequentially
# 12 connections total over 2s (2.0-4.0), then hidden nodes activate (4.0-5.0)

status_label.text.set_onward(2.0, 'Computing hidden layer activations...')

num_ih = len(ih_connections)
conn_dur = 2.0 / num_ih  # time per connection lighting up

for idx, (i, j, conn) in enumerate(ih_connections):
    t_light = 2.0 + idx * conn_dur
    conn.set_stroke(color=COLOR_CONN_ON, start=t_light, end=t_light + 0.1)
    conn.set_opacity(1.0, start=t_light, end=t_light + 0.15)

# Hidden nodes activate after connections (4.0 - 5.0)
HIDDEN_VALUES = [0.72, 0.45, 0.91, 0.33]
for j in range(len(HIDDEN_YS)):
    t_act = 4.0 + j * 0.2
    hidden_nodes[j].set_fill(color=COLOR_ACTIVE, start=t_act, end=t_act + 0.2)
    hidden_nodes[j].set_stroke(color=COLOR_ACTIVE, start=t_act, end=t_act + 0.2)
    hidden_nodes[j].pulsate(start=t_act, end=t_act + 0.6, scale_factor=1.15, n_pulses=1)
    hidden_value_labels[j].text.set_onward(t_act, str(HIDDEN_VALUES[j]))
    hidden_value_labels[j].set_opacity(1.0, start=t_act, end=t_act + 0.2)

# -- Phase 3 (5-8s): Hidden -> Output propagation ----------------------------
status_label.text.set_onward(5.0, 'Computing output layer activations...')

num_ho = len(ho_connections)
conn_dur_ho = 2.0 / num_ho

for idx, (j, k, conn) in enumerate(ho_connections):
    t_light = 5.0 + idx * conn_dur_ho
    conn.set_stroke(color=COLOR_CONN_ON, start=t_light, end=t_light + 0.1)
    conn.set_opacity(1.0, start=t_light, end=t_light + 0.15)

# Output nodes activate (7.0 - 8.0)
for k in range(len(OUTPUT_YS)):
    t_act = 7.0 + k * 0.3
    output_nodes[k].set_fill(color=COLOR_ACTIVE, start=t_act, end=t_act + 0.2)
    output_nodes[k].set_stroke(color=COLOR_ACTIVE, start=t_act, end=t_act + 0.2)
    output_nodes[k].pulsate(start=t_act, end=t_act + 0.6, scale_factor=1.15, n_pulses=1)
    output_value_labels[k].text.set_onward(t_act, str(OUTPUT_VALUES[k]))
    output_value_labels[k].set_opacity(1.0, start=t_act, end=t_act + 0.2)

# -- Phase 4 (8-10s): Classification result ----------------------------------
status_label.text.set_onward(8.0, 'Applying softmax to output...')

# Output node 1 (0.87) -> green (positive class)
output_nodes[0].set_fill(color=COLOR_OUTPUT_POS, start=8.5, end=8.7)
output_nodes[0].set_stroke(color=COLOR_OUTPUT_POS, start=8.5, end=8.7)
output_nodes[0].pulsate(start=8.5, end=10.0, scale_factor=1.12, n_pulses=2)

# Output node 2 (0.13) -> red (negative class)
output_nodes[1].set_fill(color=COLOR_OUTPUT_NEG, start=8.5, end=8.7)
output_nodes[1].set_stroke(color=COLOR_OUTPUT_NEG, start=8.5, end=8.7)

# Output class labels next to the nodes
class_a_label = Text(
    text='Class A', x=OUTPUT_X + NODE_R + 70, y=OUTPUT_YS[0] + 7,
    font_size=22, fill=COLOR_OUTPUT_POS, stroke_width=0, text_anchor='middle',
    creation=9.0,
)
class_a_label.fadein(9.0, 9.5)

class_b_label = Text(
    text='Class B', x=OUTPUT_X + NODE_R + 70, y=OUTPUT_YS[1] + 7,
    font_size=22, fill=COLOR_OUTPUT_NEG, stroke_width=0, text_anchor='middle',
    creation=9.0,
)
class_b_label.fadein(9.0, 9.5)

# -- Phase 5 (10-12s): Final classification label ----------------------------
status_label.text.set_onward(10.0, '')

class_label.text.set_onward(10.0, 'Classification: Class A (87%)')
class_label.set_opacity(1.0, start=10.0, end=10.5)

# Pulse the result label
class_label.pulsate(start=10.5, end=T, scale_factor=1.05, n_pulses=2)

# Final summary
summary_label = Text(
    text='Input [0.8, 0.3, 0.6]  -->  Class A with 87% confidence',
    x=960, y=900,
    font_size=22, fill=COLOR_LABEL, stroke_width=0, text_anchor='middle',
    creation=10.5,
)
summary_label.fadein(10.5, 11.0)

# Keep all nodes pulsing gently at the end
for node in input_nodes + hidden_nodes:
    node.pulsate(start=10.5, end=T, scale_factor=1.04, n_pulses=2)

# -- Add everything to canvas -------------------------------------------------
canvas.add(title, subtitle)
canvas.add(input_label, hidden_label, output_label)
canvas.add(status_label, class_label, summary_label)
canvas.add(class_a_label, class_b_label)

# Connections first (behind nodes)
for _, _, conn in ih_connections:
    canvas.add(conn)
for _, _, conn in ho_connections:
    canvas.add(conn)

# Nodes on top of connections
for node in input_nodes:
    canvas.add(node)
for node in hidden_nodes:
    canvas.add(node)
for node in output_nodes:
    canvas.add(node)

# Value labels on top of everything
for label in input_value_labels:
    canvas.add(label)
for label in hidden_value_labels:
    canvas.add(label)
for label in output_value_labels:
    canvas.add(label)

canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
