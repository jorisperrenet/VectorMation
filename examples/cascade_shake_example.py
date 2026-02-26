import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/cascade_shake')
canvas.set_background()

title = Text(text='Cascade, Shake & Slope Field', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Cascade effect: group of circles fading in with overlap
_circle_colors = ['#FF6B6B', '#FF9E6B', '#FFD06B', '#83C167',
                  '#58C4DD', '#6B8CFF', '#B06BFF', '#FF6BCD']
circles = VGroup(
    *[Circle(r=30, cx=200 + i * 80, cy=200, fill=_circle_colors[i],
             fill_opacity=0.8, stroke_width=0) for i in range(8)]
)
circles.cascade('fadein', start=0.5, end=2.5, overlap=0.5)

# Cascade write effect on rectangles
_rect_colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D',
                '#3B1F2B', '#44BBA4', '#E94F37', '#393E41']
rects = VGroup(
    *[Rectangle(width=60, height=40, x=200 + i * 80, y=300,
                fill=_rect_colors[i], fill_opacity=0.8,
                stroke_width=0) for i in range(8)]
)
rects.cascade('write', start=1, end=3.5, overlap=0.6)

# Shake effect on a text label (like an error)
error_label = Text(text='Error!', x=960, y=420, font_size=36,
                   fill='#FF6B6B', stroke_width=0, text_anchor='middle')
error_label.fadein(2, 2.5)
error_label.shake(start=2.5, end=2.8, amplitude=12, frequency=25)
error_label.shake(start=4, end=4.2, amplitude=6, frequency=20)

# Slope field for dy/dx = -x/y (circles)
ax = Axes(x_range=(-3, 3), y_range=(-3, 3),
          plot_width=600, plot_height=400,
          x=650, y=530)
ax.add_coordinates()
ax.fadein(1, 2)

slope_field = ax.get_slope_field(lambda x, y: -x / y if abs(y) > 0.1 else 0,
                                  x_step=0.5, y_step=0.5, length=0.35,
                                  stroke='#83C167')
slope_field.fadein(2, 3.5)

canvas.add_objects(circles, rects, error_label, ax, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
