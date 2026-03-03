"""Demo of statistical and advanced axes visualization methods:
plot_normal, plot_exponential, add_boxplot, plot_line_graph,
add_confidence_band, add_threshold_line, add_reference_band,
add_mean_line, add_data_labels, plot_bubble, plot_area, etc."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import Axes, Text, VectorMathAnim, parse_args

v = VectorMathAnim('/tmp')

# ── Section 1: Normal & Exponential distributions (0-3s) ──────
title1 = Text(text='Normal & Exponential Distributions', x=960, y=60,
              font_size=28, text_anchor='middle', creation=0)
title1.fadeout(start=3, end=3.3)
v.add(title1)

ax1 = Axes(x_range=(-4, 4, 1), y_range=(0, 0.5, 0.1),
           x=60, y=120, plot_width=600, plot_height=380, creation=0)
v.add(ax1)
ax1.plot_normal(mean=0, std=1, color='#4FC3F7')
ax1.add_mean_line(lambda x: math.exp(-x*x/2) / math.sqrt(2*math.pi),
                  x_range=(-4, 4), creation=0)

ax2 = Axes(x_range=(0, 5, 1), y_range=(0, 1.2, 0.2),
           x=1020, y=120, plot_width=600, plot_height=380, creation=0)
v.add(ax2)
ax2.plot_exponential(rate=1, color='#FF8A65')
ax2.plot_uniform(a=1, b=3, color='#81C784', creation=0)

# ── Section 2: Line graph with data labels (3-6s) ─────────────
title2 = Text(text='Line Graph with Data Labels', x=960, y=60,
              font_size=28, text_anchor='middle', creation=3)
title2.fadeout(start=6, end=6.3)
v.add(title2)

ax3 = Axes(x_range=(0, 6, 1), y_range=(0, 50, 10),
           x=160, y=120, plot_width=1200, plot_height=400, creation=3)
v.add(ax3)

x_vals = [1, 2, 3, 4, 5]
y_vals = [10, 25, 18, 42, 35]
ax3.plot_line_graph(x_vals, y_vals, creation=3, stroke='#4FC3F7')
ax3.add_data_labels(x_vals, y_vals, creation=3)
ax3.add_threshold_line(30, label='Target', creation=3, stroke='#F48FB1')
ax3.add_reference_band(15, 35, axis='y', creation=3,
                       fill='#4FC3F7', fill_opacity=0.1)

# ── Section 3: Box plot and confidence band (6-9s) ────────────
title3 = Text(text='Box Plot & Confidence Band', x=960, y=60,
              font_size=28, text_anchor='middle', creation=6)
title3.fadeout(start=9, end=9.3)
v.add(title3)

ax4 = Axes(x_range=(0, 4, 1), y_range=(0, 100, 20),
           x=60, y=120, plot_width=600, plot_height=380, creation=6)
v.add(ax4)
data_groups = [[20, 35, 40, 55, 65], [30, 45, 50, 60, 80], [10, 25, 35, 45, 70]]
ax4.add_boxplot(data_groups, creation=6)

ax5 = Axes(x_range=(0, 7, 1), y_range=(-2, 2, 0.5),
           x=1020, y=120, plot_width=600, plot_height=380, creation=6)
v.add(ax5)
ax5.plot(math.sin, creation=6, stroke='#4FC3F7')
ax5.add_confidence_band(
    lambda x: math.sin(x) - 0.5,
    lambda x: math.sin(x) + 0.5,
    creation=6, fill='#4FC3F7', fill_opacity=0.2)

# ── Section 4: Bubble plot and area (9-12s) ───────────────────
title4 = Text(text='Bubble Plot & Area Fill', x=960, y=60,
              font_size=28, text_anchor='middle', creation=9)
title4.fadeout(start=12, end=12.3)
v.add(title4)

ax6 = Axes(x_range=(0, 10, 2), y_range=(0, 10, 2),
           x=60, y=120, plot_width=600, plot_height=380, creation=9)
v.add(ax6)
bx = [1, 3, 5, 7, 9]
by = [2, 8, 4, 6, 3]
bsizes = [10, 25, 15, 30, 20]
ax6.plot_bubble(bx, by, bsizes, creation=9, fill='#CE93D8', fill_opacity=0.6)

ax7 = Axes(x_range=(0, 7, 1), y_range=(-1.5, 1.5, 0.5),
           x=1020, y=120, plot_width=600, plot_height=380, creation=9)
v.add(ax7)
ax7.plot_area(math.sin, x_range=(0, 2*math.pi), creation=9,
              fill='#81C784', fill_opacity=0.4)

# ── Section 5: Inflection, critical pts, function label (12-15s)
title5 = Text(text='Inflection Points & Labels', x=960, y=60,
              font_size=28, text_anchor='middle', creation=12)
v.add(title5)

ax8 = Axes(x_range=(-3, 3, 1), y_range=(-5, 5, 1),
           x=60, y=120, plot_width=600, plot_height=380, creation=12)
v.add(ax8)
cubic = lambda x: x**3 - 3*x
ax8.plot(cubic, creation=12, stroke='#FFE082')
ax8.add_inflection_points(cubic, creation=12)
ax8.get_critical_points(cubic, creation=12)

ax9 = Axes(x_range=(0, 7, 1), y_range=(-1.5, 1.5, 0.5),
           x=1020, y=120, plot_width=600, plot_height=380, creation=12)
v.add(ax9)
sin_curve = ax9.plot(math.sin, creation=12, stroke='#4FC3F7')
ax9.add_function_label(sin_curve, 'sin(x)', x_pos=2, creation=12)
ax9.annotate_area(sin_curve, x_range=(0, math.pi), label='A', creation=12,
                  color='#CE93D8')

if __name__ == '__main__':
    args = parse_args()
        v.browser_display(start=args.start or 0, end=args.end or 15,
                          fps=args.fps, port=args.port)
