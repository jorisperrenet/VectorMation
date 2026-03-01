"""Data Visualization Showcase — BarChart, PieChart, DonutChart, and WaterfallChart.

Demonstrates bar chart growth with value animation, pie chart with sector
highlighting, donut chart value morphing, and waterfall chart for cumulative
positive/negative data.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/data_visualization')
canvas.set_background()

T = 12.0

# -- Colors -------------------------------------------------------------------
BLUE   = '#58C4DD'
RED    = '#FC6255'
GREEN  = '#83C167'
YELLOW = '#F5C542'
PURPLE = '#9B72AC'
COLORS = [BLUE, RED, GREEN, YELLOW, PURPLE]

# =============================================================================
# Phase 1: BarChart (0 – 3s)
# =============================================================================
bar_title = Text(
    text='Quarterly Revenue ($M)', x=960, y=70, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
bar_title.fadein(0.0, 0.4)
bar_title.fadeout(2.5, 3.0)
canvas.add(bar_title)

bar = BarChart(
    values=[32, 45, 28, 61, 53],
    labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
    colors=COLORS,
    x=260, y=140, width=1400, height=620,
)
bar.fadein(0.0, 0.3)
bar.grow_from_zero(start=0.2, end=1.4, stagger=True, delay=0.12)
bar.add_value_labels(fmt='${:.0f}M', offset=14, font_size=22, creation=1.4)
bar.animate_values([50, 38, 65, 42, 70], start=1.8, end=2.6)
bar.fadeout(2.6, 3.0)
canvas.add(bar)

# =============================================================================
# Phase 2: PieChart (3 – 6s)
# =============================================================================
pie_title = Text(
    text='Market Share by Region', x=960, y=70, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=3.0,
)
pie_title.fadein(3.0, 3.4)
pie_title.fadeout(5.5, 6.0)
canvas.add(pie_title)

pie = PieChart(
    values=[35, 25, 20, 12, 8],
    labels=['North America', 'Europe', 'Asia', 'LATAM', 'Other'],
    colors=COLORS,
    cx=960, cy=520, r=230,
    creation=3.0,
)
pie.fadein(3.0, 3.5)
pie.sweep_in(start=3.2, end=4.4)
pie.highlight_sector(0, start=4.6, end=5.2, pull_distance=25)
pie.highlight_sector(3, start=5.0, end=5.6, pull_distance=25)
pie.fadeout(5.6, 6.0)
canvas.add(pie)

pie_sub = Text(
    text='FY 2025 Distribution', x=960, y=830, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=3.0,
)
pie_sub.fadein(3.5, 3.8)
pie_sub.fadeout(5.5, 6.0)
canvas.add(pie_sub)

# =============================================================================
# Phase 3: DonutChart (6 – 9s)
# =============================================================================
donut_title = Text(
    text='Budget Allocation', x=960, y=70, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=6.0,
)
donut_title.fadein(6.0, 6.4)
donut_title.fadeout(8.5, 9.0)
canvas.add(donut_title)

donut = DonutChart(
    values=[40, 25, 20, 10, 5],
    labels=['Eng', 'Sales', 'Ops', 'HR', 'Legal'],
    colors=COLORS,
    cx=960, cy=520, r=230, inner_radius=120,
    center_text='100%',
    creation=6.0,
)
donut.fadein(6.0, 6.6)
# Morph to new allocation
donut.animate_values([25, 30, 15, 20, 10], start=7.0, end=8.0)
donut.highlight_sector(1, start=8.0, end=8.6, pull_distance=20)
donut.fadeout(8.5, 9.0)
canvas.add(donut)

donut_sub = Text(
    text='Before / After Reorg', x=960, y=830, font_size=22,
    fill='#888', stroke_width=0, text_anchor='middle', creation=6.0,
)
donut_sub.fadein(6.5, 6.8)
donut_sub.fadeout(8.5, 9.0)
canvas.add(donut_sub)

# =============================================================================
# Phase 4: WaterfallChart (9 – 12s)
# =============================================================================
wf_title = Text(
    text='Profit Waterfall Analysis', x=960, y=50, font_size=40,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=9.0,
)
wf_title.fadein(9.0, 9.4)
wf_title.fadeout(11.5, 12.0)
canvas.add(wf_title)

waterfall = WaterfallChart(
    values=[120, 45, -30, -15, 60, -25],
    labels=['Revenue', 'Services', 'COGS', 'OpEx', 'Growth', 'Tax', 'Net'],
    x=180, y=120, width=1560, height=700,
    pos_color=GREEN, neg_color=RED, total_color=BLUE,
    font_size=18,
    show_total=True,
    creation=9.0,
)
waterfall.fadein(9.0, 9.8)
waterfall.fadeout(11.5, 12.0)
canvas.add(waterfall)

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
