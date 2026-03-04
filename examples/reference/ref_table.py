"""Table with row and column labels."""
from vectormation.objects import *

v = VectorMathAnim()
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

v.show(end=0)
