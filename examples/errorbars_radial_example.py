import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/errorbars_radial')
canvas.set_background()

title = Text(text='Error Bars, Regression & Radial Layout', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with data and error bars
ax = Axes(x_range=(0, 7), y_range=(0, 10),
          plot_width=500, plot_height=350,
          x=100, y=180)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

x_data = [1, 2, 3, 4, 5, 6]
y_data = [1.5, 3.2, 4.1, 5.8, 7.2, 8.5]
y_err = [0.5, 0.8, 0.4, 0.9, 0.6, 0.7]

# Scatter points
scatter = ax.plot_scatter(x_data, y_data, r=5, fill='#FF6B6B', creation=1.5)
scatter.fadein(1.5, 2)

# Error bars
errorbars = ax.add_error_bars(x_data, y_data, y_err, stroke='#aaa', creation=2)
errorbars.fadein(2, 2.5)

# Regression line
reg = ax.add_regression_line(x_data, y_data, stroke='#83C167', creation=2.5)
reg.fadein(2.5, 3)

# Radial layout demo
dots = VCollection(
    *[Dot(cx=1450, cy=550, r=15,
          fill=['#FF6B6B', '#83C167', '#58C4DD', '#FFFF00', '#FF79C6', '#B8BB26'][i])
      for i in range(6)]
)
dots.fadein(3, 3.5)

radial_label = Text(text='Radial Layout', x=1450, y=380,
                    font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
radial_label.fadein(3, 3.5)

dots.distribute_radial(cx=1450, cy=550, radius=100,
                        start_time=3.5, end_time=4.5)

# Swirl one dot
dots[0].swirl(start=5, end=6, turns=2)

canvas.add_objects(ax, title, dots, radial_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
