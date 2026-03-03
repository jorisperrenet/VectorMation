"""Tables & Matrices Demo — Table, Matrix, DecimalMatrix, IntegerMatrix, TexObject."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/tables_matrices')
canvas.set_background()
T = 12.0

# -- Colors -------------------------------------------------------------------
BLUE   = '#58C4DD'
GREEN  = '#83C167'
YELLOW = '#F5C542'
RED    = '#FC6255'
PURPLE = '#9B72AC'

# =============================================================================
# Phase 1: Tables (0 – 4s)
# =============================================================================

phase1_title = Text(
    text='Tables', x=960, y=60, font_size=44,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
phase1_title.fadein(0.0, 0.3)
phase1_title.fadeout(3.5, 4.0)
canvas.add(phase1_title)

# Create a data table with column and row labels
table_data = [
    ['Python',     '1991', 'Guido',   'Dynamic'],
    ['Rust',       '2010', 'Graydon', 'Static'],
    ['JavaScript', '1995', 'Brendan', 'Dynamic'],
]
table = Table(
    table_data,
    col_labels=['Language', 'Year', 'Creator', 'Typing'],
    x=310, y=120, cell_width=180, cell_height=55, font_size=22,
    creation=0,
)
table.fadein(0.2, 0.8)
canvas.add(table)

# Highlight individual cells and rows
table.highlight_cell(0, 0, start=1.0, end=1.8, color=BLUE)
table.highlight_row(1, start=1.8, end=2.5, color=GREEN)
table.highlight_column(1, start=2.4, end=3.1, color=YELLOW)

# Add a new row with animation
table.add_row(['Go', '2009', 'Rob', 'Static'], start=2.8)

# Animate cell value change
table.set_cell_value(2, 1, '1995*', start=3.2)

# Fade out the table
table.fadeout(3.5, 4.0)

# =============================================================================
# Phase 2: Matrices (4 – 8s)
# =============================================================================

phase2_title = Text(
    text='Matrices', x=960, y=60, font_size=44,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
phase2_title.fadein(4.0, 4.3)
phase2_title.fadeout(7.5, 8.0)
canvas.add(phase2_title)

# Standard Matrix
mat_label = Text(
    text='Matrix A', x=380, y=140, font_size=28,
    fill=BLUE, stroke_width=0, text_anchor='middle',
)
mat_label.fadein(4.2, 4.5)
mat_label.fadeout(7.5, 8.0)
canvas.add(mat_label)

mat = Matrix(
    [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]],
    x=380, y=320, font_size=34,
    creation=4.0,
)
mat.fadein(4.2, 4.8)
canvas.add(mat)

# Highlight diagonal entries
mat.highlight_entry(0, 0, start=5.0, end=5.6, color=YELLOW)
mat.highlight_entry(1, 1, start=5.2, end=5.8, color=YELLOW)
mat.highlight_entry(2, 2, start=5.4, end=6.0, color=YELLOW)

# Set row colors
mat.set_row_colors(BLUE, GREEN, RED, start=6.2)

# Swap rows with arc animation
mat.swap_rows(0, 2, start=6.5, end=7.2)

mat.fadeout(7.5, 8.0)

# DecimalMatrix on the right side
dec_label = Text(
    text='DecimalMatrix', x=960, y=140, font_size=28,
    fill=GREEN, stroke_width=0, text_anchor='middle',
)
dec_label.fadein(4.2, 4.5)
dec_label.fadeout(7.5, 8.0)
canvas.add(dec_label)

dec_mat = DecimalMatrix(
    [[3.14159, 2.71828],
     [1.41421, 1.73205]],
    decimals=2, x=960, y=320, font_size=34,
    creation=4.0,
)
dec_mat.fadein(4.3, 4.9)
canvas.add(dec_mat)

dec_mat.highlight_row(0, start=5.5, end=6.2, color=GREEN)
dec_mat.highlight_column(1, start=6.0, end=6.7, color=PURPLE)
dec_mat.fadeout(7.5, 8.0)

# IntegerMatrix on the far right
int_label = Text(
    text='IntegerMatrix', x=1540, y=140, font_size=28,
    fill=RED, stroke_width=0, text_anchor='middle',
)
int_label.fadein(4.2, 4.5)
int_label.fadeout(7.5, 8.0)
canvas.add(int_label)

int_mat = IntegerMatrix(
    [[10, 20],
     [30, 40]],
    x=1540, y=320, font_size=34,
    creation=4.0,
)
int_mat.fadein(4.4, 5.0)
canvas.add(int_mat)

# Row operation: R0 += 2 * R1
int_mat.row_operation(0, 1, scalar=2, start=5.8, end=6.5)
int_mat.set_column_colors(YELLOW, RED, start=6.8)
int_mat.fadeout(7.5, 8.0)

# Augmented matrix at the bottom
aug_label = Text(
    text='Augmented [A|b]', x=960, y=480, font_size=28,
    fill=YELLOW, stroke_width=0, text_anchor='middle',
)
aug_label.fadein(4.4, 4.7)
aug_label.fadeout(7.5, 8.0)
canvas.add(aug_label)

aug_mat = Matrix.augmented(
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    [[5], [3], [7]],
    x=960, y=660, font_size=30,
    creation=4.0,
)
aug_mat.fadein(4.5, 5.1)
aug_mat.fadeout(7.5, 8.0)
canvas.add(aug_mat)

# =============================================================================
# Phase 3: Text composites (8 – 12s)
# =============================================================================

phase3_title = Text(
    text='Text Composites', x=960, y=60, font_size=44,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
phase3_title.fadein(8.0, 8.3)
phase3_title.fadeout(11.5, 12.0)
canvas.add(phase3_title)

# NumberedList on the left
nlist = NumberedList(
    'Create objects',
    'Add animations',
    'Render to SVG',
    'Export video',
    x=100, y=170, font_size=30,
    creation=8.0,
)
nlist.fadein(8.2, 8.7)
nlist.fadeout(11.5, 12.0)
canvas.add(nlist)

# BulletedList in the center
blist = BulletedList(
    'Tables & grids',
    'Matrix algebra',
    'Code display',
    'Numbered lists',
    x=700, y=170, font_size=30,
    creation=8.0,
)
blist.fadein(8.4, 8.9)
blist.fadeout(11.5, 12.0)
canvas.add(blist)

# Code block on the right / bottom area
code_text = """\
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b"""

code = Code(
    code_text, language='python',
    x=100, y=430, font_size=22,
    creation=8.0,
)
code.fadein(8.5, 9.2)
canvas.add(code)

# Highlight specific code lines sequentially
hl1 = code.highlight_lines([1, 2, 3], start=9.5, end=10.3, color=BLUE, opacity=0.25)
canvas.add(hl1)

hl2 = code.highlight_lines([5, 6], start=10.2, end=11.0, color=GREEN, opacity=0.25)
canvas.add(hl2)

code.fadeout(11.5, 12.0)

# ---------------------------------------------------------------------------
canvas.browser_display(start=args.start or 0, end=args.end or T, fps=args.fps, port=args.port)
