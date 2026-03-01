"""Charts Overview Demo — GaugeChart, ProgressBar, SparkLine, TreeMap, WaffleChart, FunnelChart."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/charts_overview')
canvas.set_background()
T = 12.0

# =============================================================================
# Phase 1 (0-4s): Gauge charts and progress indicators
# =============================================================================

phase1_title = Text(
    text='Gauges & Progress Indicators', x=960, y=60, font_size=38,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
phase1_title.fadein(0.0, 0.5)
phase1_title.fadeout(3.5, 4.0)
canvas.add(phase1_title)

# -- GaugeChart (left) --------------------------------------------------------
# Create a gauge at 72% showing "Performance"
gauge = GaugeChart(
    value=72, min_val=0, max_val=100,
    x=350, y=420, radius=170,
    label='Performance', font_size=32,
)
gauge.fadein(0.2, 1.0)
gauge.fadeout(3.5, 4.2)
canvas.add(gauge)

gauge_lbl = Text(
    text='GaugeChart', x=350, y=170, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle',
)
gauge_lbl.fadein(0.3, 0.8)
gauge_lbl.fadeout(3.5, 4.0)
canvas.add(gauge_lbl)

# -- CircularProgressBar (center) ---------------------------------------------
# Animate from 0 to 87 by creating it at 0 and then using the arc end_angle
cpb = CircularProgressBar(
    value=87, x=960, y=420, radius=90, stroke_width=14,
    bar_color='#4ECDC4', font_size=40,
)
cpb.fadein(0.5, 1.2)
cpb.grow_from_center(start=0.5, end=2.0)
cpb.fadeout(3.5, 4.2)
canvas.add(cpb)

cpb_lbl = Text(
    text='CircularProgressBar', x=960, y=570, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle',
)
cpb_lbl.fadein(0.6, 1.0)
cpb_lbl.fadeout(3.5, 4.0)
canvas.add(cpb_lbl)

# -- ProgressBar (right) ------------------------------------------------------
# A horizontal progress bar that fills from 0 to ~90%
pbar = ProgressBar(
    width=350, height=28, x=1380, y=380,
    fill_color='#E84D60', bg_color='#2a2a3a', corner_radius=8,
)
pbar.set_progress(0.0, start=0)
pbar.set_progress(0.92, start=0.8, end=2.8)
pbar.fadein(0.5, 1.0)
pbar.fadeout(3.5, 4.2)
canvas.add(pbar)

pbar_pct = Text(
    text='92%', x=1555, y=440, font_size=30,
    fill='#E84D60', stroke_width=0, text_anchor='middle', creation=2.8,
)
pbar_pct.fadein(2.8, 3.2)
pbar_pct.fadeout(3.5, 4.0)
canvas.add(pbar_pct)

pbar_lbl = Text(
    text='ProgressBar', x=1555, y=340, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle',
)
pbar_lbl.fadein(0.6, 1.0)
pbar_lbl.fadeout(3.5, 4.0)
canvas.add(pbar_lbl)

# =============================================================================
# Phase 2 (4-8s): Specialized charts
# =============================================================================

phase2_title = Text(
    text='Specialized Charts', x=960, y=60, font_size=38,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=4.0,
)
phase2_title.fadein(4.0, 4.5)
phase2_title.fadeout(7.5, 8.0)
canvas.add(phase2_title)

# -- SparkLine (top-left) -----------------------------------------------------
spark_data = [3, 7, 4, 8, 2, 9, 5, 11, 6, 13, 8, 10, 14, 12, 16]
spark = SparkLine(
    data=spark_data, x=100, y=200, width=300, height=80,
    stroke='#58C4DD', stroke_width=2.5, show_endpoint=True,
    creation=4.0,
)
spark.fadein(4.2, 4.8)
spark.fadeout(7.5, 8.0)
canvas.add(spark)

spark_lbl = Text(
    text='SparkLine', x=250, y=160, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=4.0,
)
spark_lbl.fadein(4.2, 4.7)
spark_lbl.fadeout(7.5, 8.0)
canvas.add(spark_lbl)

spark_ctx = Text(
    text='Revenue Trend', x=250, y=310, font_size=18,
    fill='#aaa', stroke_width=0, text_anchor='middle', creation=4.5,
)
spark_ctx.fadein(4.5, 5.0)
spark_ctx.fadeout(7.5, 8.0)
canvas.add(spark_ctx)

# -- TreeMap (center-right) ----------------------------------------------------
treemap = TreeMap(
    data=[
        ('Web', 42), ('Mobile', 28), ('Desktop', 18),
        ('API', 8), ('IoT', 4),
    ],
    x=480, y=140, width=520, height=380,
    font_size=16, creation=4.0,
)
treemap.fadein(4.4, 5.2)
treemap.fadeout(7.5, 8.2)
canvas.add(treemap)

tm_lbl = Text(
    text='TreeMap', x=740, y=120, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=4.0,
)
tm_lbl.fadein(4.4, 4.9)
tm_lbl.fadeout(7.5, 8.0)
canvas.add(tm_lbl)

# -- FunnelChart (right) -------------------------------------------------------
funnel = FunnelChart(
    stages=[
        ('Visitors', 10000),
        ('Signups', 5200),
        ('Trials', 2800),
        ('Paid', 1100),
        ('Retained', 650),
    ],
    x=1080, y=140, width=420, height=380,
    font_size=16, gap=5, creation=4.0,
)
funnel.fadein(4.6, 5.4)
funnel.fadeout(7.5, 8.2)
canvas.add(funnel)

fn_lbl = Text(
    text='FunnelChart', x=1290, y=120, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=4.0,
)
fn_lbl.fadein(4.6, 5.0)
fn_lbl.fadeout(7.5, 8.0)
canvas.add(fn_lbl)

# -- WaffleChart (bottom) -----------------------------------------------------
waffle = WaffleChart(
    categories=[
        ('Chrome', 65, '#4ECDC4'),
        ('Firefox', 18, '#E84D60'),
        ('Safari', 12, '#F5A623'),
        ('Other', 5, '#9B59B6'),
    ],
    x=140, y=560, grid_size=10, cell_size=16, gap=2,
    font_size=13, creation=4.0,
)
waffle.fadein(5.0, 5.8)
waffle.fadeout(7.5, 8.2)
canvas.add(waffle)

wf_lbl = Text(
    text='WaffleChart', x=230, y=540, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=4.0,
)
wf_lbl.fadein(5.0, 5.4)
wf_lbl.fadeout(7.5, 8.0)
canvas.add(wf_lbl)

# =============================================================================
# Phase 3 (8-12s): More chart types
# =============================================================================

phase3_title = Text(
    text='Metrics & Comparisons', x=960, y=60, font_size=38,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=8.0,
)
phase3_title.fadein(8.0, 8.5)
phase3_title.fadeout(11.5, 12.0)
canvas.add(phase3_title)

# -- Scoreboard (top-left) ----------------------------------------------------
scoreboard = Scoreboard(
    entries=[
        ('Revenue', '$4.2M'),
        ('Users', '128K'),
        ('Uptime', '99.97%'),
        ('NPS', '+72'),
    ],
    x=80, y=120, col_width=180, row_height=70,
    font_size=30, creation=8.0,
)
scoreboard.fadein(8.2, 9.0)
scoreboard.fadeout(11.5, 12.0)
canvas.add(scoreboard)

sb_lbl = Text(
    text='Scoreboard', x=440, y=105, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=8.0,
)
sb_lbl.fadein(8.2, 8.7)
sb_lbl.fadeout(11.5, 12.0)
canvas.add(sb_lbl)

# -- KPICard row (top-right) ---------------------------------------------------
kpi1 = KPICard(
    title='Monthly Active Users', value='128,340',
    subtitle='+12.4% vs last month',
    trend_data=[80, 85, 82, 90, 95, 92, 100, 108, 115, 120, 125, 128],
    x=840, y=120, width=300, height=160,
    font_size=40, creation=8.0,
)
kpi1.fadein(8.3, 9.0)
kpi1.fadeout(11.5, 12.0)
canvas.add(kpi1)

kpi2 = KPICard(
    title='Avg Response Time', value='42ms',
    subtitle='-8.7% improvement',
    trend_data=[65, 58, 55, 52, 48, 50, 45, 44, 43, 42],
    x=1180, y=120, width=300, height=160,
    font_size=40, creation=8.0,
)
kpi2.fadein(8.5, 9.2)
kpi2.fadeout(11.5, 12.0)
canvas.add(kpi2)

kpi_lbl = Text(
    text='KPICard', x=1180, y=105, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=8.0,
)
kpi_lbl.fadein(8.3, 8.8)
kpi_lbl.fadeout(11.5, 12.0)
canvas.add(kpi_lbl)

# -- BulletChart row (middle) -------------------------------------------------
bullet1 = BulletChart(
    actual=270, target=250,
    ranges=[(200, '#1a2a3a'), (280, '#2a3a4a'), (350, '#3a4a5a')],
    label='Revenue', x=250, y=350, width=600, height=35,
    bar_color='#58C4DD', max_val=350,
    font_size=16, creation=8.0,
)
bullet1.fadein(8.6, 9.3)
bullet1.fadeout(11.5, 12.0)
canvas.add(bullet1)

bullet2 = BulletChart(
    actual=180, target=220,
    ranges=[(150, '#1a2a3a'), (230, '#2a3a4a'), (300, '#3a4a5a')],
    label='Profit', x=250, y=410, width=600, height=35,
    bar_color='#F5A623', max_val=300,
    font_size=16, creation=8.0,
)
bullet2.fadein(8.8, 9.5)
bullet2.fadeout(11.5, 12.0)
canvas.add(bullet2)

bullet3 = BulletChart(
    actual=92, target=85,
    ranges=[(60, '#1a2a3a'), (80, '#2a3a4a'), (100, '#3a4a5a')],
    label='Satisfaction', x=250, y=470, width=600, height=35,
    bar_color='#4ECDC4', max_val=100,
    font_size=16, creation=8.0,
)
bullet3.fadein(9.0, 9.7)
bullet3.fadeout(11.5, 12.0)
canvas.add(bullet3)

bc_lbl = Text(
    text='BulletChart', x=550, y=330, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=8.0,
)
bc_lbl.fadein(8.6, 9.0)
bc_lbl.fadeout(11.5, 12.0)
canvas.add(bc_lbl)

# -- CalendarHeatmap (bottom-left) ---------------------------------------------
import random
random.seed(42)
cal_data = [random.randint(0, 12) for _ in range(7 * 26)]

cal = CalendarHeatmap(
    data=cal_data, rows=7, cols=26,
    x=80, y=560, cell_size=11, gap=2,
    creation=8.0,
)
cal.fadein(9.0, 9.8)
cal.fadeout(11.5, 12.0)
canvas.add(cal)

cal_lbl = Text(
    text='CalendarHeatmap', x=260, y=540, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=8.0,
)
cal_lbl.fadein(9.0, 9.4)
cal_lbl.fadeout(11.5, 12.0)
canvas.add(cal_lbl)

# -- MatrixHeatmap (bottom-right) ----------------------------------------------
matrix_data = [
    [1.0, 0.8, 0.2, 0.1],
    [0.8, 1.0, 0.5, 0.3],
    [0.2, 0.5, 1.0, 0.7],
    [0.1, 0.3, 0.7, 1.0],
]
mheat = MatrixHeatmap(
    data=matrix_data,
    row_labels=['A', 'B', 'C', 'D'],
    col_labels=['A', 'B', 'C', 'D'],
    x=920, y=540, cell_size=50, gap=3,
    font_size=14, creation=8.0,
)
mheat.fadein(9.2, 10.0)
mheat.fadeout(11.5, 12.0)
canvas.add(mheat)

mh_lbl = Text(
    text='MatrixHeatmap', x=1100, y=520, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=8.0,
)
mh_lbl.fadein(9.2, 9.6)
mh_lbl.fadeout(11.5, 12.0)
canvas.add(mh_lbl)

# -- BoxPlot (bottom far-right) ------------------------------------------------
bp_data = [
    [2, 4, 5, 7, 8, 9, 11, 12, 14],
    [3, 5, 6, 7, 8, 10, 12, 13, 15, 18],
    [1, 3, 4, 5, 6, 7, 8, 9, 10],
]
boxplot = BoxPlot(
    data_groups=bp_data,
    x=1400, y=520, plot_width=250, plot_height=220, box_width=35,
    box_color='#9B59B6', median_color='#FF6B6B',
    font_size=12, creation=8.0,
)
boxplot.fadein(9.4, 10.2)
boxplot.fadeout(11.5, 12.0)
canvas.add(boxplot)

bp_lbl = Text(
    text='BoxPlot', x=1525, y=505, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=8.0,
)
bp_lbl.fadein(9.4, 9.8)
bp_lbl.fadeout(11.5, 12.0)
canvas.add(bp_lbl)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
