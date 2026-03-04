"""Table with row and column labels."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

table = Table(
    data=[
        ['Python', '1991', 'Guido'],
        ['Rust',   '2010', 'Graydon'],
        ['Zig',    '2015', 'Andrew'],
    ],
    col_labels=['Language', 'Year', 'Creator'],
    x=560, y=300,
    cell_width=200, cell_height=60, font_size=28,
)

v.add(table)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_table.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
