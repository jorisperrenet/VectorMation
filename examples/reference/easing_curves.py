"""Easing function curves diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
from vectormation.easings import smooth, linear, rush_into, rush_from, there_and_back, ease_in_out_cubic
args = parse_args()

W, H = 520, 360
v = VectorMathAnim('_ref_out', verbose=args.verbose, width=W, height=H)
v.set_background(fill='#1e1e2e')

PLOT_W, PLOT_H = 140, 100
PAD_X, PAD_Y = 30, 18
START_X, START_Y = 35, 40

easings = [
    ('linear', linear, '#89b4fa'),
    ('smooth', smooth, '#a6e3a1'),
    ('rush_into', rush_into, '#f38ba8'),
    ('rush_from', rush_from, '#f9e2af'),
    ('there_and_back', there_and_back, '#cba6f7'),
    ('ease_in_out_cubic', ease_in_out_cubic, '#fab387'),
]

for idx, (name, func, color) in enumerate(easings):
    row, col = divmod(idx, 3)
    ox = START_X + col * (PLOT_W + PAD_X)
    oy = START_Y + row * (PLOT_H + PAD_Y + 20)

    v.add(
        Line(x1=ox, y1=oy + PLOT_H, x2=ox + PLOT_W, y2=oy + PLOT_H, stroke='#45475a', stroke_width=1),
        Line(x1=ox, y1=oy, x2=ox, y2=oy + PLOT_H, stroke='#45475a', stroke_width=1),
    )

    v.add(
        Text('0', x=ox - 10, y=oy + PLOT_H + 4, font_size=8, fill='#585b70'),
        Text('1', x=ox + PLOT_W - 3, y=oy + PLOT_H + 12, font_size=8, fill='#585b70'),
        Text('1', x=ox - 10, y=oy + 5, font_size=8, fill='#585b70'),
    )

    N = 60
    pts = []
    for i in range(N + 1):
        t = i / N
        val = func(t)
        px = ox + t * PLOT_W
        py = oy + PLOT_H - val * PLOT_H
        pts.append((px, py))

    v.add(Lines(*pts, stroke=color, stroke_width=2, fill_opacity=0))
    v.add(Text(name, x=ox + PLOT_W // 2 - len(name) * 3, y=oy - 6, font_size=11, fill=color))

v.add(Text('Easing Functions', x=195, y=20, font_size=14, fill='#cdd6f4'))

if args.for_docs:
    v.write_frame(filename='docs/source/_static/images/easing_curves.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
