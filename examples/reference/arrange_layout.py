"""arrange / distribute layout diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

W, H = 500, 320
v = VectorMathAnim('_ref_out', verbose=args.verbose, width=W, height=H)
v.set_background(fill='#1e1e2e')

# --- arrange (top half) ---
v.add(Text("arrange(direction='right', buff=12)", x=125, y=22, font_size=12, fill='#cdd6f4'))

colors = ['#f38ba8', '#89b4fa', '#a6e3a1', '#f9e2af']
sizes = [(50, 35), (40, 35), (60, 35), (45, 35)]
start_x = 95
y_top = 45
buff = 12

x = start_x
for i, ((w, h), c) in enumerate(zip(sizes, colors)):
    v.add(Rectangle(w, h, x=x, y=y_top,
                    fill=c, fill_opacity=0.25, stroke=c, stroke_width=1.8))
    if i < len(sizes) - 1:
        bx = x + w
        v.add(
            DashedLine(x1=bx, y1=y_top + h + 2, x2=bx, y2=y_top + h + 12, dash='2,2', stroke='#585b70', stroke_width=0.6),
            DashedLine(x1=bx + buff, y1=y_top + h + 2, x2=bx + buff, y2=y_top + h + 12, dash='2,2', stroke='#585b70', stroke_width=0.6),
        )
    x += w + buff

v.add(
    Arrow(x1=start_x - 30, y1=y_top + 17, x2=start_x - 8, y2=y_top + 17,
          tip_length=6, tip_width=5, stroke='#585b70', stroke_width=1),
    Text('→', x=x + 5, y=y_top + 22, font_size=14, fill='#585b70'),
)

# --- arrange down (middle) ---
v.add(Text("arrange(direction='down')", x=155, y=112, font_size=12, fill='#cdd6f4'))

y = 130
col_x = 200
for i, ((w, h), c) in enumerate(zip(sizes[:3], colors[:3])):
    v.add(Rectangle(w, h, x=col_x, y=y,
                    fill=c, fill_opacity=0.25, stroke=c, stroke_width=1.8))
    y += h + buff

# --- arrange_in_grid (right side) ---
v.add(Text("arrange_in_grid(rows=2, cols=2)", x=290, y=112, font_size=12, fill='#cdd6f4'))

grid_x, grid_y = 320, 130
grid_w, grid_h = 45, 30
for row in range(2):
    for col in range(2):
        idx = row * 2 + col
        gx = grid_x + col * (grid_w + buff)
        gy = grid_y + row * (grid_h + buff)
        v.add(Rectangle(grid_w, grid_h, x=gx, y=gy,
                        fill=colors[idx], fill_opacity=0.25, stroke=colors[idx], stroke_width=1.8))

if args.for_docs:
    v.write_frame(filename='docs/source/_static/images/arrange.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
