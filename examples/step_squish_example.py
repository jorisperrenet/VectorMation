import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/step_squish')
canvas.set_background()

title = Text(text='Step Plot, Squish & Stagger FadeIn', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with step function
ax = Axes(x_range=(0, 8), y_range=(0, 10),
          plot_width=700, plot_height=400,
          x=150, y=180)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

# Step function data
xs = [0, 1, 2, 3, 4, 5, 6, 7]
ys = [2, 2, 5, 5, 3, 7, 7, 4]
step = ax.plot_step(xs, ys, stroke='#83C167', stroke_width=3)
step.create(1.5, 2.5)

# Horizontal labels
lbl1 = ax.add_horizontal_label(5, 'threshold', side='right', fill='#FF6B6B')
lbl1.fadein(2.5, 3)

# Highlight the y-range
band = ax.highlight_y_range(4, 6, fill='#FF6B6B', fill_opacity=0.1)
band.fadein(2.5, 3)

# Right side: squish demo
label2 = Text(text='Squish Effects', x=1400, y=200,
              font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
label2.fadein(3, 3.5)

circle = Circle(cx=1400, cy=350, r=50, fill='#83C167', fill_opacity=0.4,
                stroke='#83C167', stroke_width=2)
circle.fadein(3, 3.5)
circle.squish(start=3.5, end=4.5, axis='x', factor=0.3)

rect = Rectangle(100, 60, x=1350, y=430, fill='#FF6B6B', fill_opacity=0.4,
                  stroke='#FF6B6B', stroke_width=2)
rect.fadein(3, 3.5)
rect.squish(start=4, end=5, axis='y', factor=0.4)

# Stagger fadein demo at bottom
items = VCollection(
    Dot(cx=0, cy=0, r=12, fill='#58C4DD'),
    Dot(cx=0, cy=0, r=12, fill='#83C167'),
    Dot(cx=0, cy=0, r=12, fill='#FF6B6B'),
    Dot(cx=0, cy=0, r=12, fill='#FFFF00'),
    Dot(cx=0, cy=0, r=12, fill='#FF79C6'),
)
items.arrange(direction=RIGHT, buff=40)
items.center_to_pos(960, 750, start=0)
items.stagger_fadein(start=5, end=6.5, shift_dir=UP, shift_amount=30, overlap=0.3)

canvas.add_objects(ax, title, circle, rect, items, label2)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
