import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/radar_chart')
canvas.set_background()

title = Text(text='Radar Chart', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

chart = RadarChart(
    values=[85, 70, 90, 60, 95, 75],
    labels=['Speed', 'Power', 'Accuracy', 'Defense', 'Stamina', 'Agility'],
    max_val=100,
    cx=960, cy=520, radius=280, font_size=20,
)
chart.stagger('fadein', delay=0.05, start=0.5, end=1)

canvas.add_objects(chart, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
