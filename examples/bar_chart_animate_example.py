import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/bar_chart_animate')
canvas.set_background()

# Sales data by quarter
chart = BarChart(
    values=[30, 45, 28, 60, 52],
    labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
    colors=['#58C4DD', '#83C167', '#FC6255', '#FFFF00', '#9A72AC'],
    x=240, y=120, width=1200, height=700,
)
chart.fadein(0, 1)

# Animate to new values (growth scenario)
chart.animate_values([50, 65, 55, 80, 90], start=2, end=3.5)

title = Text(text='Quarterly Sales Growth', x=960, y=60,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(chart, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
