import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/highlight_range')
canvas.set_background()

title = Text(text='Highlight X-Range & Line From-To', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with highlighted region and lines
ax = Axes(x_range=(-2, 6), y_range=(-2, 12),
          plot_width=900, plot_height=500,
          x=200, y=200)
ax.add_coordinates()
ax_title = ax.add_title('Integration Region', font_size=28, fill='#58C4DD')
ax.fadein(0.5, 1.5)

f = lambda x: 0.5 * x ** 2
curve = ax.plot(f, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

# Highlight x-range [1, 4]
strip = ax.highlight_x_range(1, 4, fill='#83C167', fill_opacity=0.15)
strip.fadein(2.5, 3)

# Get area under curve in that range
area = ax.get_area(f, x_range=(1, 4), fill='#83C167', fill_opacity=0.3)
area.fadein(3, 4)

# Lines marking the boundaries
line1 = ax.get_line_from_to(1, 0, 1, f(1), stroke='#FF6B6B', stroke_width=2)
line2 = ax.get_line_from_to(4, 0, 4, f(4), stroke='#FF6B6B', stroke_width=2)
line1.fadein(2.5, 3)
line2.fadein(2.5, 3)

# Annotate
ann = ax.add_arrow_annotation(2.5, f(2.5) + 2, 'Area = ∫₁⁴ ½x² dx',
                               direction='down', fill='#fff', stroke='#fff')
ann.fadein(4, 4.5)

canvas.add_objects(ax, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
