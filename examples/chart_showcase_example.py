"""Showcase of chart types: RadarChart, GaugeChart, SparkLine, KPICard, WaffleChart."""
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/chart_showcase')

title = Text("Chart Showcase", x=960, y=50, font_size=40, fill='#fff')
title.fadein(start=0, end=0.5)

# --- RadarChart ---
rc = RadarChart(
    labels=["Speed", "Power", "Range", "Armor", "Magic"],
    values=[0.8, 0.6, 0.9, 0.5, 0.7],
    x=300, y=350, radius=150,
    fill='#3498DB', fill_opacity=0.3, stroke='#3498DB',
)
rc.fadein(start=0.5, end=1.5)

# --- GaugeChart ---
gc = GaugeChart(value=0.72, x=750, y=350, radius=130,
                fill='#E74C3C', track_fill='#1e1e2e',
                label='CPU Usage')
gc.fadein(start=1, end=2)

# --- SparkLine ---
sl = SparkLine(values=[3, 7, 2, 8, 5, 9, 4, 6, 8, 3],
               x=1100, y=280, width=300, height=80,
               stroke='#2ECC71', stroke_width=2)
sl.fadein(start=1.5, end=2.5)

# --- WaffleChart ---
wc = WaffleChart(value=0.65, x=200, y=700, rows=5, cols=10,
                 cell_size=25, fill='#F39C12', empty_fill='#1e1e2e')
wc.fadein(start=2, end=3)

# --- KPICard ---
kpi = KPICard(title='Revenue', value='$1.2M', x=700, y=650,
              width=250, height=120, fill='#2C3E50', text_fill='#ECF0F1')
kpi.fadein(start=2.5, end=3.5)

# Fade everything out
for obj in [title, rc, gc, sl, wc, kpi]:
    obj.fadeout(start=8.5, end=9.5)

v.add(title, rc, gc, sl, wc, kpi)
v.browser_display(end=args.duration or 10, fps=args.fps, port=args.port, hot_reload=args.hot_reload)
