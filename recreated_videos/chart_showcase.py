"""Chart Types Showcase — PieChart, BarChart, RadarChart."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/chart_showcase')
canvas.set_background()

T = 12.0

# -- Colors -------------------------------------------------------------------
COLORS = ['#E84D60', '#F5A623', '#4ECDC4', '#58C4DD', '#9B59B6']

# =============================================================================
# Phase 1: PieChart (0 – 4s)
# =============================================================================
pie_title = Text(
    text='Revenue by Region', x=960, y=80, font_size=42,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
pie_title.fadein(0.0, 0.5)
pie_title.fadeout(3.5, 4.0)
canvas.add(pie_title)

pie = PieChart(
    values=[35, 25, 20, 12, 8],
    labels=['APAC', 'EMEA', 'AMER', 'LATAM', 'MEA'],
    colors=COLORS,
    cx=960, cy=520, r=220,
)
pie.sweep_in(start=0.3, end=1.8)
pie.fadein(0.3, 1.0)
pie.highlight_sector(0, start=2.0, end=3.0, pull_distance=25)
pie.fadeout(3.5, 4.2)
canvas.add(pie)

# Subtitle showing percentage
pie_sub = Text(
    text='Q4 2025 Breakdown', x=960, y=830, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle',
)
pie_sub.fadein(1.0, 1.5)
pie_sub.fadeout(3.5, 4.0)
canvas.add(pie_sub)

# =============================================================================
# Phase 2: BarChart (4 – 8s)
# =============================================================================
bar_title = Text(
    text='Monthly Sales ($K)', x=960, y=80, font_size=42,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=4.0,
)
bar_title.fadein(4.0, 4.5)
bar_title.fadeout(7.5, 8.0)
canvas.add(bar_title)

bar = BarChart(
    values=[48, 62, 55, 78, 91, 85],
    labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    colors=['#E84D60', '#F5A623', '#4ECDC4', '#58C4DD', '#9B59B6', '#83C167'],
    x=260, y=160, width=1400, height=640,
    creation=4.0,
)
bar.fadein(4.0, 4.5)
bar.grow_from_zero(start=4.2, end=5.8, stagger=True, delay=0.15)
bar.add_value_labels(fmt='${:.0f}K', offset=14, font_size=22, creation=5.8)
# Animate bars to new values
bar.animate_values([52, 70, 60, 95, 110, 102], start=6.2, end=7.2)
bar.fadeout(7.5, 8.2)
canvas.add(bar)

# =============================================================================
# Phase 3: RadarChart (8 – 12s)
# =============================================================================
radar_title = Text(
    text='Team Skills Assessment', x=960, y=60, font_size=42,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=8.0,
)
radar_title.fadein(8.0, 8.5)
radar_title.fadeout(11.0, 11.5)
canvas.add(radar_title)

radar = RadarChart(
    values=[85, 70, 90, 60, 75, 80],
    labels=['Design', 'Backend', 'Frontend', 'DevOps', 'Testing', 'Strategy'],
    max_val=100,
    colors=['#4ECDC4'],
    cx=960, cy=540, radius=220,
    fill_opacity=0.3,
    creation=8.0,
)
radar.fadein(8.0, 8.8)

# Add a second dataset for comparison
radar.add_dataset(
    values=[60, 90, 65, 85, 80, 55],
    color='#E84D60',
    fill_opacity=0.25,
    creation=9.5,
)
radar.fadeout(11.0, 11.8)
canvas.add(radar)

# Legend labels
legend_a = Text(
    text='Team Alpha', x=1320, y=820, font_size=22,
    fill='#4ECDC4', stroke_width=0, text_anchor='start', creation=8.5,
)
legend_a.fadein(8.5, 9.0)
legend_a.fadeout(11.0, 11.5)
canvas.add(legend_a)

legend_b = Text(
    text='Team Beta', x=1320, y=855, font_size=22,
    fill='#E84D60', stroke_width=0, text_anchor='start', creation=9.5,
)
legend_b.fadein(9.5, 10.0)
legend_b.fadeout(11.0, 11.5)
canvas.add(legend_b)

# Legend dots
dot_a = Dot(cx=1305, cy=814, fill='#4ECDC4', creation=8.5)
dot_a.fadein(8.5, 9.0)
dot_a.fadeout(11.0, 11.5)
canvas.add(dot_a)

dot_b = Dot(cx=1305, cy=849, fill='#E84D60', creation=9.5)
dot_b.fadein(9.5, 10.0)
dot_b.fadeout(11.0, 11.5)
canvas.add(dot_b)

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
