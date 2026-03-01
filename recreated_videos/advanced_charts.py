"""Advanced Charts Demo — GanttChart, GaugeChart, MatrixHeatmap, BoxPlot."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/advanced_charts')
canvas.set_background()

T = 12.0

# =============================================================================
# Phase 1 (0-3s): Title + GanttChart
# =============================================================================
title = Text(
    text='Advanced Charts', x=960, y=70, font_size=48,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
title.fadein(0.0, 0.5)
title.fadeout(2.5, 3.0)
canvas.add(title)

gantt_label = Text(
    text='Project Timeline', x=960, y=140, font_size=28,
    fill='#888', stroke_width=0, text_anchor='middle',
)
gantt_label.fadein(0.2, 0.7)
gantt_label.fadeout(2.5, 3.0)
canvas.add(gantt_label)

gantt = GanttChart(
    tasks=[
        ('Research',  0, 3, '#E84D60'),
        ('Design',    2, 5, '#F5A623'),
        ('Develop',   4, 9, '#4ECDC4'),
        ('Testing',   7, 10, '#58C4DD'),
    ],
    x=260, y=200, width=1400,
    bar_height=50, bar_spacing=20, font_size=20,
)
gantt.fadein(0.3, 1.0)
gantt.fadeout(2.5, 3.0)
canvas.add(gantt)

# =============================================================================
# Phase 2 (3-6s): GaugeChart + CircularProgressBar
# =============================================================================
gauge_label = Text(
    text='Performance Gauge', x=500, y=140, font_size=28,
    fill='#888', stroke_width=0, text_anchor='middle', creation=3.0,
)
gauge_label.fadein(3.0, 3.5)
gauge_label.fadeout(5.5, 6.0)
canvas.add(gauge_label)

gauge = GaugeChart(
    value=72, min_val=0, max_val=100,
    x=500, y=480, radius=180,
    label='Speed', font_size=36,
    creation=3.0,
)
gauge.fadein(3.0, 3.8)
gauge.fadeout(5.5, 6.0)
canvas.add(gauge)

progress_label = Text(
    text='Upload Progress', x=1400, y=300, font_size=24,
    fill='#888', stroke_width=0, text_anchor='middle', creation=3.0,
)
progress_label.fadein(3.0, 3.5)
progress_label.fadeout(5.5, 6.0)
canvas.add(progress_label)

# Build a CircularProgressBar that visually "fills" from 0% to 87%
progress = CircularProgressBar(
    value=87, x=1400, y=500, radius=100, stroke_width=14,
    bar_color='#4ECDC4', font_size=40,
    creation=3.0,
)
# Animate the progress arc from zero sweep to final value
# The progress arc is the second object (index 1) — an Arc
if len(progress.objects) >= 2:
    prog_arc = progress.objects[1]  # the progress Arc
    final_angle = prog_arc.end_angle.at_time(3.0)  # 90 - 360*0.87
    prog_arc.end_angle.set_onward(3.0, 90)          # start at 0% (same as start_angle)
    prog_arc.end_angle.move_to(3.5, 5.3, final_angle, stay=True)
progress.fadein(3.0, 3.8)
progress.fadeout(5.5, 6.0)
canvas.add(progress)

# =============================================================================
# Phase 3 (6-9s): MatrixHeatmap (4x4 correlation matrix)
# =============================================================================
heatmap_title = Text(
    text='Correlation Matrix', x=960, y=100, font_size=38,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=6.0,
)
heatmap_title.fadein(6.0, 6.5)
heatmap_title.fadeout(8.5, 9.0)
canvas.add(heatmap_title)

corr_data = [
    [1.0,  0.8,  0.3, -0.2],
    [0.8,  1.0,  0.5,  0.1],
    [0.3,  0.5,  1.0,  0.7],
    [-0.2, 0.1,  0.7,  1.0],
]
labels = ['A', 'B', 'C', 'D']

heatmap = MatrixHeatmap(
    data=corr_data,
    row_labels=labels,
    col_labels=labels,
    x=560, y=180, cell_size=100, gap=4,
    font_size=22, show_values=True,
    creation=6.0,
)
heatmap.fadein(6.0, 6.8)
heatmap.fadeout(8.5, 9.0)
canvas.add(heatmap)

# =============================================================================
# Phase 4 (9-12s): BoxPlot
# =============================================================================
box_title = Text(
    text='Distribution Analysis', x=960, y=80, font_size=38,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=9.0,
)
box_title.fadein(9.0, 9.5)
box_title.fadeout(11.5, 12.0)
canvas.add(box_title)

box_data = [
    [12, 15, 18, 22, 25, 28, 30, 35, 40],       # Group 1
    [20, 25, 30, 32, 35, 38, 42, 48, 55],       # Group 2
    [8, 10, 14, 16, 18, 20, 22, 24, 27],        # Group 3
    [30, 35, 38, 40, 42, 45, 50, 55, 62, 70],   # Group 4
]

boxplot = BoxPlot(
    data_groups=box_data,
    x=360, y=150, plot_width=1200, plot_height=700,
    box_width=60, box_color='#58C4DD', median_color='#E84D60',
    font_size=18, creation=9.0,
)
boxplot.fadein(9.0, 9.8)
boxplot.fadeout(11.5, 12.0)
canvas.add(boxplot)

# Group labels beneath position numbers
group_names = ['Control', 'Treatment A', 'Treatment B', 'Treatment C']
for i, name in enumerate(group_names):
    lbl = Text(
        text=name, x=660 + i * 300, y=900, font_size=16,
        fill='#aaa', stroke_width=0, text_anchor='middle', creation=9.0,
    )
    lbl.fadein(9.2, 9.8)
    lbl.fadeout(11.5, 12.0)
    canvas.add(lbl)

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
