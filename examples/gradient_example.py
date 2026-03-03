import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(width=1200, height=600, verbose=args.verbose, save_dir='svgs/gradient')
canvas.set_background()

# Create gradients
sunset = LinearGradient([
    (0, '#FC6255'),
    (0.5, '#F0AC5F'),
    (1, '#FFFF00'),
])
canvas.add_def(sunset)

ocean = LinearGradient([
    (0, '#1e3a5f'),
    (0.5, '#58C4DD'),
    (1, '#5CD0B3'),
], x1='0%', y1='100%', x2='0%', y2='0%')  # vertical
canvas.add_def(ocean)

glow = RadialGradient([
    (0, '#FFFF00', 1),
    (0.5, '#FC6255', 0.6),
    (1, '#1e1e2e', 0),
])
canvas.add_def(glow)

# Apply gradients to shapes — evenly spaced across the canvas
col_w = 1200 // 3
shape_size = 200

r1 = Rectangle(shape_size, shape_size, x=col_w * 0 + (col_w - shape_size) // 2, y=180,
               fill=sunset.fill_ref(), fill_opacity=1, stroke_width=0)

r2 = Rectangle(shape_size, shape_size, x=col_w * 1 + (col_w - shape_size) // 2, y=180,
               fill=ocean.fill_ref(), fill_opacity=1, stroke_width=0)

c1 = Circle(r=shape_size // 2, cx=col_w * 2 + col_w // 2, cy=180 + shape_size // 2,
            fill=glow.fill_ref(), fill_opacity=1, stroke_width=0)

# Labels
l1 = Text(text='Linear (horizontal)', x=col_w * 0 + col_w // 2, y=420, font_size=22,
          fill='#aaa', stroke_width=0, text_anchor='middle')
l2 = Text(text='Linear (vertical)', x=col_w * 1 + col_w // 2, y=420, font_size=22,
          fill='#aaa', stroke_width=0, text_anchor='middle')
l3 = Text(text='Radial', x=col_w * 2 + col_w // 2, y=420, font_size=22,
          fill='#aaa', stroke_width=0, text_anchor='middle')

title = Text(text='SVG Gradient Support', x=600, y=80,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')

canvas.add_objects(r1, r2, c1, l1, l2, l3, title)

if args.for_docs:
    canvas.write_frame(filename='docs/source/_static/videos/gradient_example.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
