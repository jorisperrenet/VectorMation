"""Matrix Operations — inspired by 3Blue1Brown's Essence of Linear Algebra.

Demonstrates elementary row operations, row scaling, row swaps,
and matrix transpose on a 3x3 matrix with visual highlighting.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/matrix_operations')
v.set_background(fill='#1a1a2e')

# -- Colors -------------------------------------------------------------------
COL_TITLE    = '#e0e0ff'
COL_SUBTITLE = '#8888cc'
COL_LABEL    = '#aaaacc'
COL_ROW1     = '#FF6B6B'   # coral red
COL_ROW2     = '#4ECDC4'   # teal
COL_ROW3     = '#FFE66D'   # warm yellow
COL_ACCENT   = '#A78BFA'   # purple
COL_SUCCESS  = '#6BCB77'   # green
COL_HIGHLIGHT = '#FFD700'  # gold

# -- Timeline -----------------------------------------------------------------
# 0-1.5    : Title fade in
# 1.5-3    : Matrix appears
# 3-5      : Highlight rows one by one
# 5-8      : Row scaling (R1 *= 2)
# 8-11     : Row operation (R3 += -2*R1)
# 11-14    : Row swap (R1 <-> R2)
# 14-17    : Highlight columns
# 17-21    : Matrix transpose
# 21-23    : Final state + fadeout

TOTAL = 23.0

# ── Title ────────────────────────────────────────────────────────────────────
title = Text(text='Matrix Operations', x=960, y=80,
             font_size=52, fill=COL_TITLE, stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 1.0)

subtitle = Text(text='Elementary Row Operations & Transpose', x=960, y=135,
                font_size=26, fill=COL_SUBTITLE, stroke_width=0,
                text_anchor='middle', creation=0)
subtitle.fadein(0.3, 1.2)

# ── 3x3 Matrix ──────────────────────────────────────────────────────────────
data = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

m = Matrix(data, x=960, y=500, font_size=42, h_spacing=100, v_spacing=65, creation=0)
m.fadein(1.5, 2.5)

# ── Operation labels (reusable text that changes content) ────────────────────
op_label = Text(text='', x=960, y=820,
                font_size=32, fill=COL_LABEL, stroke_width=0,
                text_anchor='middle', creation=0)

detail_label = Text(text='', x=960, y=870,
                    font_size=24, fill='#777799', stroke_width=0,
                    text_anchor='middle', creation=0)

# ═══════════════════════════════════════════════════════════════════════════════
# Section 1: Highlight rows one by one (t = 3..5)
# ═══════════════════════════════════════════════════════════════════════════════
op_label.text.set_onward(2.8, 'Identifying Matrix Rows')
op_label.fadein(2.8, 3.2)

# Row labels that appear next to the matrix
row_labels = []
for i, (color, name) in enumerate([(COL_ROW1, 'R1'), (COL_ROW2, 'R2'), (COL_ROW3, 'R3')]):
    lbl = Text(text=name, x=780, y=453 + i * 65,
               font_size=28, fill=color, stroke_width=0,
               text_anchor='middle', creation=0)
    lbl.fadein(3.0 + i * 0.5, 3.3 + i * 0.5)
    row_labels.append(lbl)

# Highlight each row in sequence
m.highlight_row(0, start=3.0, end=3.8, color=COL_ROW1)
m.highlight_row(1, start=3.6, end=4.4, color=COL_ROW2)
m.highlight_row(2, start=4.2, end=5.0, color=COL_ROW3)

# ═══════════════════════════════════════════════════════════════════════════════
# Section 2: Row scaling — multiply R1 by 2 (t = 5..8)
# ═══════════════════════════════════════════════════════════════════════════════
op_label.text.set_onward(5.0, 'Row Scaling: R1 <- 2 * R1')
detail_label.text.set_onward(5.0, 'Multiply every entry in Row 1 by scalar 2')
detail_label.fadein(5.0, 5.5)

# Highlight row 1 as it's being scaled
m.highlight_row(0, start=5.2, end=6.5, color=COL_HIGHLIGHT)

# Animate the scalar multiplication by updating each entry
# Row 0: [1, 2, 3] -> [2, 4, 6]
for c in range(3):
    old_val = data[0][c]
    new_val = old_val * 2
    entry = m.entries[0][c]
    # Animate number counting up
    entry.text.set(5.8, 7.0,
        lambda t, _s=5.8, _d=1.2, _ov=old_val, _nv=new_val:
            str(int(round(_ov + (_nv - _ov) * min(1, max(0, (t - _s) / _d))))),
        stay=True)

# Flash the scaled row in success color
m.highlight_row(0, start=7.0, end=7.8, color=COL_SUCCESS)

# Update data tracking
data[0] = [2, 4, 6]

# ═══════════════════════════════════════════════════════════════════════════════
# Section 3: Row operation — R3 += (-2) * R1 (t = 8..11)
# ═══════════════════════════════════════════════════════════════════════════════
op_label.text.set_onward(8.0, 'Row Operation: R3 <- R3 + (-2) * R1')
detail_label.text.set_onward(8.0, 'Subtract twice Row 1 from Row 3')

# Highlight source row (R1) in purple
m.highlight_row(0, start=8.3, end=9.5, color=COL_ACCENT)

# Highlight target row (R3) in yellow
m.highlight_row(2, start=8.5, end=9.5, color=COL_HIGHLIGHT)

# Perform the row operation: R3 += (-2)*R1
# Current state: R1 = [2, 4, 6], R3 = [7, 8, 9]
# Result: R3 = [7-4, 8-8, 9-12] = [3, 0, -3]
m.row_operation(target_row=2, source_row=0, scalar=-2, start=9.0, end=10.5)

# Flash the result row
m.highlight_row(2, start=10.5, end=11.0, color=COL_SUCCESS)

# Update data tracking
data[2] = [3, 0, -3]

# ═══════════════════════════════════════════════════════════════════════════════
# Section 4: Row swap — R1 <-> R2 (t = 11..14)
# ═══════════════════════════════════════════════════════════════════════════════
op_label.text.set_onward(11.0, 'Row Swap: R1 <-> R2')
detail_label.text.set_onward(11.0, 'Exchange Row 1 and Row 2 positions')

# Highlight both rows before swap
m.highlight_row(0, start=11.3, end=12.0, color=COL_ROW1)
m.highlight_row(1, start=11.3, end=12.0, color=COL_ROW2)

# Animate the row swap with arc paths
m.swap_rows(0, 1, start=12.0, end=13.2)

# Update row labels
row_labels[0].set_fill(color=COL_ROW2, start=12.0)
row_labels[0].text.set_onward(12.0, 'R2')
row_labels[1].set_fill(color=COL_ROW1, start=12.0)
row_labels[1].text.set_onward(12.0, 'R1')

# Flash the swapped rows
m.highlight_row(0, start=13.2, end=13.8, color=COL_SUCCESS)
m.highlight_row(1, start=13.2, end=13.8, color=COL_SUCCESS)

# Update data tracking
data[0], data[1] = data[1], data[0]
# Now: [[4, 5, 6], [2, 4, 6], [3, 0, -3]]

# ═══════════════════════════════════════════════════════════════════════════════
# Section 5: Highlight columns (t = 14..17)
# ═══════════════════════════════════════════════════════════════════════════════
op_label.text.set_onward(14.0, 'Identifying Matrix Columns')
detail_label.text.set_onward(14.0, 'Each column is a vector in the column space')

# Fade out row labels
for lbl in row_labels:
    lbl.fadeout(14.0, 14.5)

# Column labels
col_colors = ['#FF6B6B', '#4ECDC4', '#FFE66D']
col_labels = []
for i, (color, name) in enumerate(zip(col_colors, ['C1', 'C2', 'C3'])):
    lbl = Text(text=name, x=860 + i * 100, y=350,
               font_size=28, fill=color, stroke_width=0,
               text_anchor='middle', creation=0)
    lbl.fadein(14.3 + i * 0.4, 14.6 + i * 0.4)
    col_labels.append(lbl)

# Highlight each column in sequence
m.highlight_column(0, start=14.5, end=15.3, color=col_colors[0])
m.highlight_column(1, start=15.1, end=15.9, color=col_colors[1])
m.highlight_column(2, start=15.7, end=16.5, color=col_colors[2])

# Highlight diagonal entries
op_label.text.set_onward(16.5, 'Matrix Diagonal')
detail_label.text.set_onward(16.5, 'The main diagonal entries')
m.highlight_entry(0, 0, start=16.5, end=17.2, color=COL_HIGHLIGHT)
m.highlight_entry(1, 1, start=16.7, end=17.2, color=COL_HIGHLIGHT)
m.highlight_entry(2, 2, start=16.9, end=17.2, color=COL_HIGHLIGHT)

# ═══════════════════════════════════════════════════════════════════════════════
# Section 6: Matrix transpose (t = 17..21)
# ═══════════════════════════════════════════════════════════════════════════════

# Fade out column labels
for lbl in col_labels:
    lbl.fadeout(17.0, 17.5)

op_label.text.set_onward(17.2, 'Matrix Transpose: A -> A^T')
detail_label.text.set_onward(17.2, 'Rows become columns, columns become rows')

# Show the original matrix label
orig_label = Text(text='A =', x=780, y=500,
                  font_size=36, fill='#ccccee', stroke_width=0,
                  text_anchor='middle', creation=0)
orig_label.fadein(17.2, 17.8)

# To animate a transpose, we move each entry (r,c) to position (c,r)
# The Matrix class stores entries as self.entries[r][c]
# We need to compute the target positions
h_spacing = 100
v_spacing = 65
cx, cy = 960, 500  # matrix center

# Compute positions before transpose
# entry at (r, c) is at:
#   x = cx - (cols-1)*h_spacing/2 + c*h_spacing
#   y = cy - (rows-1)*v_spacing/2 + r*v_spacing + font_size*TEXT_Y_OFFSET

# For a 3x3 matrix, rows and cols are both 3, so the grid stays the same size
# Each entry (r, c) moves to position (c, r)
TEXT_Y_OFFSET_VAL = 0.35  # approximate from the source

# Animate each entry moving to its transposed position
for r in range(3):
    for c in range(3):
        if r == c:
            # Diagonal stays in place, just flash it
            m.entries[r][c].flash(start=18.0, end=19.0, color=COL_ACCENT)
            continue
        # Current position of entry (r, c)
        cur_x = cx - (3 - 1) * h_spacing / 2 + c * h_spacing
        cur_y = cy - (3 - 1) * v_spacing / 2 + r * v_spacing + 42 * TEXT_Y_OFFSET_VAL
        # Target position: where (c, r) is
        tgt_x = cx - (3 - 1) * h_spacing / 2 + r * h_spacing
        tgt_y = cy - (3 - 1) * v_spacing / 2 + c * v_spacing + 42 * TEXT_Y_OFFSET_VAL
        # Use path_arc for a curved animation
        m.entries[r][c].path_arc(tgt_x, tgt_y, start=18.0, end=19.5, angle=0.5)

# Swap the entries in the data structure
new_entries = [[m.entries[c][r] for c in range(3)] for r in range(3)]
m.entries = new_entries

# Update label
orig_label.text.set_onward(19.5, 'A^T =')
orig_label.flash(start=19.5, end=20.2, color=COL_SUCCESS)

# Flash all entries to confirm transpose
for r in range(3):
    for c in range(3):
        m.entries[r][c].flash(start=19.8, end=20.5, color=COL_SUCCESS)

# ═══════════════════════════════════════════════════════════════════════════════
# Section 7: Final display and fadeout (t = 21..23)
# ═══════════════════════════════════════════════════════════════════════════════
op_label.text.set_onward(20.5, 'Transpose Complete')
detail_label.text.set_onward(20.5, 'A^T[i][j] = A[j][i]')

# Final highlight sweep across all entries
for r in range(3):
    for c in range(3):
        m.entries[r][c].flash(start=21.0 + (r * 3 + c) * 0.1, end=21.8, color=COL_HIGHLIGHT)

# Fade everything out
title.fadeout(22.0, 22.8)
subtitle.fadeout(22.0, 22.8)
m.fadeout(22.0, 22.8)
op_label.fadeout(22.0, 22.8)
detail_label.fadeout(22.0, 22.8)
orig_label.fadeout(22.0, 22.8)

# ── Add all objects to canvas ────────────────────────────────────────────────
v.add(title, subtitle, m, op_label, detail_label, orig_label)
for lbl in row_labels:
    v.add(lbl)
for lbl in col_labels:
    v.add(lbl)

if not args.no_display:
    v.browser_display(start=args.start or 0, end=args.end or TOTAL,
                      fps=args.fps, port=args.port)
