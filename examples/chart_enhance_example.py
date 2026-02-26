import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/chart_enhance')
canvas.set_background()

title = Text(text='Chart Enhancements', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Pie Chart with highlight ---
pie = PieChart(
    values=[35, 25, 20, 15, 5],
    labels=['Python', 'JS', 'Rust', 'Go', 'Other'],
    cx=480, cy=420, r=200,
)
pie.fadein(0.5, 1)

# Highlight the largest sector
pie.highlight_sector(0, start=2, end=4, pull_distance=35)
# Then highlight another
pie.highlight_sector(2, start=3.5, end=5.5, pull_distance=35)

# --- Bar Chart with color changes ---
bar = BarChart(
    values=[70, 45, 90, 60, 80, 30],
    labels=['A', 'B', 'C', 'D', 'E', 'F'],
    x=960, y=160, width=860, height=600,
)
bar.fadein(0.5, 1)

# Highlight the tallest bar
bar.set_bar_color(2, '#FF6B6B', start=2, end=2.5)
# Animate to new values
bar.animate_values([50, 80, 40, 95, 60, 70], start=3, end=4.5)
# Color all bars
bar.set_bar_colors(['#FF6B6B', '#FFFF00', '#83C167', '#58C4DD', '#9B59B6', '#FF9500'], start=5)

canvas.add_objects(pie, bar, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
