import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/dashed_title')
canvas.set_background()

title = Text(text='Dashed Lines, Axes Title & Sequential', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with title and dashed lines
ax = Axes(x_range=(-3, 3), y_range=(-1, 10),
          plot_width=800, plot_height=400,
          x=100, y=180)
ax.add_coordinates()
ax_title = ax.add_title('Quadratic Function', font_size=28, fill='#58C4DD')
ax.fadein(0.5, 1.5)

f = lambda x: x ** 2
curve = ax.plot(f, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

# Dashed reference lines
dashed1 = ax.get_dashed_line(-2, 4, 2, 4, stroke='#FF6B6B')
dashed1.fadein(2.5, 3)
dashed2 = ax.get_dashed_line(0, 0, 0, 9, stroke='#83C167')
dashed2.fadein(3, 3.5)

# Sequential animation: squares appear one after another
squares = VGroup(
    *[Rectangle(width=50, height=50, x=1050 + (i % 4) * 70, y=200 + (i // 4) * 70,
                fill='#FF6B6B', fill_opacity=0.7, stroke_width=0) for i in range(12)]
)
squares.stagger('fadein', start=1, end=4, overlap=0)

# Shrink to point demo
dot_target = Dot(cx=1250, cy=600, r=6, fill='#FFFF00', stroke_width=0)
dot_target.fadein(3, 3.5)
for i, sq in enumerate(squares):
    sq.shrink_to_point(1250, 600, start=5 + i * 0.15, end=5.5 + i * 0.15)

canvas.add_objects(ax, squares, dot_target, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/dashed_title_example.mp4', fps=30, end=6)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
