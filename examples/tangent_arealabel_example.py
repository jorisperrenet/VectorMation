import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/tangent_arealabel')
canvas.set_background()

title = Text(text='Moving Tangent, Area Labels & Stagger Color', x=960, y=50,
             font_size=36, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Moving tangent line ---
ax = Axes(x_range=(-1, 7), y_range=(-2, 4),
          plot_width=500, plot_height=300,
          x=50, y=130)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

func = lambda x: math.sin(x) * 1.5 + 1
curve = ax.plot(func, stroke='#83C167', stroke_width=3)
curve.create(1.5, 2.5)

tangent = ax.add_moving_tangent(func, x_start=0, x_end=6, start=2, end=5,
                                 length=150, stroke='#FFFF00')
tangent.fadein(2, 2.3)

# --- Area label ---
ax2 = Axes(x_range=(0, 5), y_range=(0, 5),
           plot_width=400, plot_height=250,
           x=700, y=130)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

func2 = lambda x: 0.5 * x ** 2
curve2 = ax2.plot(func2, stroke='#FF6B6B', stroke_width=3)
curve2.create(1.5, 2.5)

area = ax2.get_area(func2, x_range=(0, 3), creation=2,
                     fill='#FF6B6B', fill_opacity=0.2)
area.fadein(2, 2.5)

label = ax2.add_area_label(func2, x_range=(0, 3), creation=2.5)
label.fadein(2.5, 3)

# --- Stagger color ---
dots = VCollection(
    *[Dot(cx=200 + i * 60, cy=700, r=20, fill='#FF6B6B')
      for i in range(10)]
)
dots.fadein(1, 1.5)
dots.stagger_color(start=2, end=5,
                    colors=('#FF6B6B', '#58C4DD', '#83C167', '#FFFF00'))

color_label = Text(text='Stagger Color', x=470, y=640,
                   font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
color_label.fadein(1, 1.5)

canvas.add_objects(ax, ax2, title, tangent, area, label, dots, color_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/tangent_arealabel_example.mp4', fps=30, end=5)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
