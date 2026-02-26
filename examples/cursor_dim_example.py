import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/cursor_dim')
canvas.set_background()

title = Text(text='Cursor, Dim/Undim & Focus Effects', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with animated cursor
ax = Axes(x_range=(-3, 3), y_range=(-1, 10),
          plot_width=700, plot_height=400,
          x=100, y=150)
ax.add_coordinates()
ax_title = ax.add_title('Moving Cursor', font_size=24, fill='#aaa')
ax.fadein(0.5, 1.5)

f = lambda x: x ** 2
curve = ax.plot(f, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

# Cursor travels along the curve
cursor = ax.add_cursor(f, x_start=-2.5, x_end=2.5, start=2.5, end=6,
                        fill='#FF6B6B', r=8)

# Dim/undim demo
r1 = Rectangle(width=120, height=80, x=950, y=200, fill='#83C167',
               stroke_width=2, stroke='#fff')
r2 = Rectangle(width=120, height=80, x=1100, y=200, fill='#FF6B6B',
               stroke_width=2, stroke='#fff')
r3 = Rectangle(width=120, height=80, x=1250, y=200, fill='#58C4DD',
               stroke_width=2, stroke='#fff')
for r in (r1, r2, r3):
    r.fadein(0.5, 1)

# Focus on r2: dim the others
dim_label = Text(text='Focus on red', x=1160, y=320, font_size=20,
                 fill='#aaa', stroke_width=0, text_anchor='middle')
dim_label.fadein(2, 2.5)

r1.dim(start=2.5, end=3)
r3.dim(start=2.5, end=3)
r2.indicate(start=3, end=3.5, scale_factor=1.15)

# Undim all
r1.undim(start=4.5, end=5)
r3.undim(start=4.5, end=5)

# Focus on r3
r1.dim(start=5.5, end=6)
r2.dim(start=5.5, end=6)
r3.indicate(start=6, end=6.5, scale_factor=1.15)

canvas.add_objects(ax, r1, r2, r3, dim_label, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
