"""Demo of advanced chart types: RadarChart, WaterfallChart, GaugeChart,
SparkLine, KPICard, BulletChart, WaffleChart, CircularProgressBar,
MatrixHeatmap, BoxPlot."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import (
    Text, VectorMathAnim, parse_args,
    RadarChart, WaterfallChart, GaugeChart, SparkLine,
    KPICard, BulletChart, WaffleChart, CircularProgressBar,
    MatrixHeatmap, BoxPlot,
)

v = VectorMathAnim('/tmp')

# ── Section 1: Radar + Waterfall (0-4s) ────────────────────────────
title1 = Text(text='RadarChart & WaterfallChart', x=960, y=50,
              font_size=28, text_anchor='middle', creation=0)
title1.fadeout(start=4, end=4.3)
v.add(title1)

radar = RadarChart(
    values=[85, 70, 95, 60, 80],
    labels=['Speed', 'Power', 'Skill', 'Defense', 'Stamina'],
    cx=400, cy=500, radius=200, creation=0,
)
radar.fadein(start=0, end=1)
v.add(radar)

waterfall = WaterfallChart(
    values=[100, -20, 50, -15, 30, -10],
    labels=['Start', 'Tax', 'Sales', 'Costs', 'Bonus', 'Fee'],
    x=800, y=150, width=800, height=350, creation=0,
)
waterfall.fadein(start=0.5, end=1.5)
v.add(waterfall)

# ── Section 2: Gauge + CircularProgress (4-8s) ─────────────────────
title2 = Text(text='GaugeChart & CircularProgressBar', x=960, y=50,
              font_size=28, text_anchor='middle', creation=4)
title2.fadeout(start=8, end=8.3)
v.add(title2)

gauge = GaugeChart(value=72, x=450, y=550, radius=180,
                   label='Speed', creation=4)
gauge.fadein(start=4, end=5)
v.add(gauge)

cpb1 = CircularProgressBar(value=0.85, x=1100, y=400, radius=100,
                           bar_color='#81C784', creation=4)
cpb1.fadein(start=4.3, end=5)
v.add(cpb1)

cpb2 = CircularProgressBar(value=0.45, x=1450, y=400, radius=100,
                           bar_color='#FF8A65', creation=4)
cpb2.fadein(start=4.6, end=5.3)
v.add(cpb2)

# ── Section 3: KPI + SparkLine + Bullet (8-12s) ────────────────────
title3 = Text(text='KPICard, SparkLine & BulletChart', x=960, y=50,
              font_size=28, text_anchor='middle', creation=8)
title3.fadeout(start=12, end=12.3)
v.add(title3)

kpi = KPICard(title='Revenue', value='$4.2M', subtitle='+12% YoY',
              trend_data=[3.1, 3.5, 3.2, 3.8, 4.0, 4.2],
              x=100, y=200, creation=8)
kpi.fadein(start=8, end=9)
v.add(kpi)

spark = SparkLine(data=[10, 25, 18, 42, 35, 50, 28, 60],
                  x=500, y=250, width=200, height=50,
                  show_endpoint=True, creation=8)
spark.fadein(start=8.3, end=9)
v.add(spark)

bullet = BulletChart(actual=275, target=300,
                     ranges=[(200, '#3a3a4a'), (250, '#4a4a5a'), (350, '#5a5a6a')],
                     label='Sales Q4', x=100, y=450, width=700, creation=8)
bullet.fadein(start=8.5, end=9.5)
v.add(bullet)

bullet2 = BulletChart(actual=180, target=220,
                      ranges=[(150, '#3a3a4a'), (200, '#4a4a5a'), (250, '#5a5a6a')],
                      label='Leads', x=100, y=550, width=700, creation=8)
bullet2.fadein(start=8.7, end=9.7)
v.add(bullet2)

# ── Section 4: Waffle + MatrixHeatmap + BoxPlot (12-16s) ───────────
title4 = Text(text='WaffleChart, MatrixHeatmap & BoxPlot', x=960, y=50,
              font_size=28, text_anchor='middle', creation=12)
v.add(title4)

waffle = WaffleChart(
    categories=[('A', 45, '#4FC3F7'), ('B', 30, '#FF8A65'), ('C', 25, '#81C784')],
    x=80, y=130, cell_size=18, gap=2, creation=12,
)
waffle.fadein(start=12, end=13)
v.add(waffle)

heatmap = MatrixHeatmap(
    data=[[1, 5, 3], [4, 2, 6], [7, 3, 1], [2, 8, 4]],
    row_labels=['Q1', 'Q2', 'Q3', 'Q4'],
    col_labels=['East', 'West', 'North'],
    x=650, y=130, cell_size=60, creation=12,
)
heatmap.fadein(start=12.3, end=13)
v.add(heatmap)

boxplot = BoxPlot(
    data_groups=[[20, 35, 40, 55, 65], [30, 45, 50, 60, 80],
                 [10, 25, 35, 45, 70], [40, 50, 55, 70, 90]],
    x=1150, y=130, plot_width=600, plot_height=400, creation=12,
)
boxplot.fadein(start=12.5, end=13.5)
v.add(boxplot)

if __name__ == '__main__':
    args = parse_args()
    if not args.no_display:
        v.browser_display(start=args.start or 0, end=args.end or 16,
                          fps=args.fps, port=args.port)
