import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/table_highlight')
canvas.set_background()

# Create a multiplication table
data = [[i * j for j in range(1, 6)] for i in range(1, 6)]
table = Table(data,
              row_labels=['1', '2', '3', '4', '5'],
              col_labels=['1', '2', '3', '4', '5'],
              cell_width=120, cell_height=60)
table.center_to_pos(960, 540)
table.fadein(0, 1)

# Highlight diagonal (perfect squares)
for i in range(5):
    table.highlight_cell(i, i, 1.5 + i * 0.3, 2.5 + i * 0.3, color='#58C4DD')

# Highlight row 2 (multiples of 3)
table.highlight_row(2, 4, 5, color='#83C167')

# Highlight column 3 (multiples of 4)
table.highlight_column(3, 5.5, 6.5, color='#FC6255')

title = Text(text='Multiplication Table', x=960, y=50,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(table, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/table_highlight_example.mp4', fps=30, end=7)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
