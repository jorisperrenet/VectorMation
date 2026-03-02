import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/kpi_bullet')
canvas.set_background()

title = Text(text='KPI Cards, Bullet Charts, Filled Step & Calendar Heatmap',
             x=960, y=40, font_size=32, fill='#58C4DD', stroke_width=0,
             text_anchor='middle')
title.write(0, 1)

# --- KPI Cards ---
kpi1 = KPICard('Revenue', '$1.2M', subtitle='+12% MoM',
               trend_data=[80, 95, 88, 110, 105, 120, 130],
               x=50, y=80, width=260, height=150)
kpi1.fadein(1, 1.5)

kpi2 = KPICard('Users', '45.2K', subtitle='+8.3% WoW',
               trend_data=[30, 35, 32, 40, 38, 42, 45],
               x=340, y=80, width=260, height=150, value_color='#83C167')
kpi2.fadein(1.2, 1.7)

kpi3 = KPICard('Latency', '23ms', subtitle='-15% vs target',
               trend_data=[40, 35, 30, 28, 25, 23, 23],
               x=630, y=80, width=260, height=150, value_color='#FF79C6')
kpi3.fadein(1.4, 1.9)

# --- Bullet Charts ---
bc1 = BulletChart(actual=270, target=250, label='Revenue',
                  ranges=[(150, '#1a2a1a'), (225, '#2a3a2a'), (300, '#3a4a3a')],
                  x=200, y=280, width=500, height=35, bar_color='#58C4DD')
bc1.fadein(2, 2.5)

bc2 = BulletChart(actual=85, target=90, label='Satisfaction',
                  ranges=[(50, '#2a1a1a'), (75, '#3a2a2a'), (100, '#4a3a3a')],
                  x=200, y=330, width=500, height=35, bar_color='#83C167')
bc2.fadein(2.2, 2.7)

bc3 = BulletChart(actual=150, target=200, label='New Users',
                  ranges=[(100, '#1a1a2a'), (175, '#2a2a3a'), (250, '#3a3a4a')],
                  x=200, y=380, width=500, height=35, bar_color='#FF6B6B')
bc3.fadein(2.4, 2.9)

# --- Filled Step Chart ---
ax = Axes(x_range=(0, 8), y_range=(0, 10),
          plot_width=350, plot_height=200, x=950, y=260)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

fs = ax.plot_filled_step([0, 1, 2, 3, 4, 5, 6, 7],
                          [2, 5, 3, 8, 4, 7, 6, 9],
                          fill='#FF79C6', fill_opacity=0.3,
                          stroke='#FF79C6')
fs.fadein(2, 3)

step_label = Text(text='Filled Step', x=1125, y=250,
                  font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
step_label.fadein(1, 1.5)

# --- Calendar Heatmap ---
import random
random.seed(42)
activity = {(r, c): random.randint(0, 10) for r in range(7) for c in range(30)}
cal = CalendarHeatmap(activity, rows=7, cols=30, x=200, y=520,
                      cell_size=12, gap=2)
cal.fadein(2.5, 3.5)

cal_label = Text(text='Calendar Heatmap (Activity)', x=500, y=500,
                 font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
cal_label.fadein(1, 1.5)

# Day labels
for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
    lbl = Text(text=day, x=185, y=520 + i * 14 + 10,
               font_size=10, fill='#666', stroke_width=0, text_anchor='end')
    lbl.fadein(2.5, 3)
    canvas.add_objects(lbl)

canvas.add_objects(title, kpi1, kpi2, kpi3, bc1, bc2, bc3,
                   ax, fs, step_label, cal, cal_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/kpi_bullet_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
