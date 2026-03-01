"""Advanced Charts Extended — SparkLine, KPICard, BulletChart, CalendarHeatmap, Scoreboard."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import random
from vectormation.objects import *

random.seed(42)

args = parse_args()
show = VectorMathAnim(verbose=args.verbose, save_dir='svgs/advanced_charts_extended')
show.set_background()

T = 15.0

# =============================================================================
# Phase 1 (0-3s): SparkLine showcase
# =============================================================================
spark_title = Text(
    text='Sparklines — Inline Trend Indicators', x=960, y=70, font_size=42,
    fill='#fff', stroke_width=0, text_anchor='middle',
)
spark_title.fadein(0.0, 0.5)
spark_title.fadeout(2.5, 3.0)
show.add(spark_title)

# Generate varied trend data
uptrend = [10, 12, 11, 15, 18, 17, 22, 25, 28, 32, 30, 35]
downtrend = [40, 38, 35, 33, 30, 28, 25, 22, 20, 18, 15, 12]
volatile = [random.randint(10, 50) for _ in range(20)]
steady = [25 + random.gauss(0, 2) for _ in range(15)]

spark_labels = ['Revenue', 'Churn', 'Volatility', 'Stability']
spark_data = [uptrend, downtrend, volatile, steady]
spark_colors = ['#4ECDC4', '#E84D60', '#F5A623', '#58C4DD']

for i, (label, data, color) in enumerate(zip(spark_labels, spark_data, spark_colors)):
    row_y = 180 + i * 100

    lbl = Text(
        text=label, x=450, y=row_y + 20, font_size=26,
        fill='#aaa', stroke_width=0, text_anchor='end',
    )
    lbl.fadein(0.2 + i * 0.15, 0.7 + i * 0.15)
    lbl.fadeout(2.5, 3.0)
    show.add(lbl)

    spark = SparkLine(
        data=data, x=500, y=row_y, width=900, height=40,
        stroke=color, stroke_width=2.5, show_endpoint=True,
    )
    spark.fadein(0.3 + i * 0.15, 0.8 + i * 0.15)
    spark.fadeout(2.5, 3.0)
    show.add(spark)

# =============================================================================
# Phase 2 (3-6s): KPICard dashboard
# =============================================================================
kpi_title = Text(
    text='KPI Dashboard', x=960, y=70, font_size=42,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=3.0,
)
kpi_title.fadein(3.0, 3.5)
kpi_title.fadeout(5.5, 6.0)
show.add(kpi_title)

kpi_configs = [
    ('Revenue', '$1.2M', '+12% YoY', [80, 85, 90, 88, 95, 102, 110, 115, 120]),
    ('Users', '48.3K', '+8.5% MoM', [30, 32, 31, 35, 38, 40, 42, 45, 48]),
    ('Conversion', '3.7%', '-0.2% WoW', [4.2, 4.0, 3.9, 3.8, 3.7, 3.8, 3.7, 3.6, 3.7]),
]

for i, (title_text, value, subtitle, trend) in enumerate(kpi_configs):
    card_x = 180 + i * 540
    card = KPICard(
        title=title_text, value=value, subtitle=subtitle,
        trend_data=trend,
        x=card_x, y=200, width=460, height=280,
        bg_color='#1a1a2e', font_size=64,
        creation=3.0,
    )
    card.fadein(3.2 + i * 0.2, 3.8 + i * 0.2)
    card.fadeout(5.5, 6.0)
    show.add(card)

# Descriptive subtitle
kpi_sub = Text(
    text='Real-time metrics with embedded sparkline trends',
    x=960, y=560, font_size=22, fill='#666', stroke_width=0,
    text_anchor='middle', creation=3.0,
)
kpi_sub.fadein(3.5, 4.0)
kpi_sub.fadeout(5.5, 6.0)
show.add(kpi_sub)

# =============================================================================
# Phase 3 (6-9s): BulletChart comparison
# =============================================================================
bullet_title = Text(
    text='Bullet Charts — Performance vs Target', x=960, y=70,
    font_size=42, fill='#fff', stroke_width=0, text_anchor='middle',
    creation=6.0,
)
bullet_title.fadein(6.0, 6.5)
bullet_title.fadeout(8.5, 9.0)
show.add(bullet_title)

bullet_configs = [
    ('Revenue', 270, 250, [(150, '#1a2a3a'), (225, '#2a3a4a'), (300, '#3a4a5a')]),
    ('Profit', 22, 25, [(12.5, '#1a2a3a'), (18.75, '#2a3a4a'), (25, '#3a4a5a')]),
    ('Satisfaction', 4.5, 4.2, [(2.1, '#1a2a3a'), (3.15, '#2a3a4a'), (5.0, '#3a4a5a')]),
    ('New Customers', 1500, 2000, [(1000, '#1a2a3a'), (1500, '#2a3a4a'), (2000, '#3a4a5a')]),
    ('Growth', 85, 80, [(40, '#1a2a3a'), (60, '#2a3a4a'), (100, '#3a4a5a')]),
]

for i, (label, actual, target, ranges) in enumerate(bullet_configs):
    row_y = 180 + i * 100
    bullet = BulletChart(
        actual=actual, target=target, ranges=ranges, label=label,
        x=350, y=row_y, width=1200, height=50,
        bar_color='#58C4DD', target_color='#E84D60',
        font_size=20, creation=6.0,
    )
    bullet.fadein(6.2 + i * 0.15, 6.8 + i * 0.15)
    bullet.fadeout(8.5, 9.0)
    show.add(bullet)

# Legend
for i, (clr, label) in enumerate([('#58C4DD', 'Actual'), ('#E84D60', 'Target')]):
    lx = 750 + i * 200
    marker = Rectangle(
        width=20, height=12, x=lx, y=790, fill=clr,
        fill_opacity=1, stroke_width=0, creation=6.0,
    )
    marker.fadein(6.5, 7.0)
    marker.fadeout(8.5, 9.0)
    show.add(marker)
    leg_lbl = Text(
        text=label, x=lx + 28, y=803, font_size=18,
        fill='#aaa', stroke_width=0, text_anchor='start', creation=6.0,
    )
    leg_lbl.fadein(6.5, 7.0)
    leg_lbl.fadeout(8.5, 9.0)
    show.add(leg_lbl)

# =============================================================================
# Phase 4 (9-12s): CalendarHeatmap (GitHub-style contribution graph)
# =============================================================================
cal_title = Text(
    text='Contribution Heatmap', x=960, y=70, font_size=42,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=9.0,
)
cal_title.fadein(9.0, 9.5)
cal_title.fadeout(11.5, 12.0)
show.add(cal_title)

# Generate 52 weeks x 7 days of contribution data
cal_data = []
for week in range(52):
    for day in range(7):
        # Simulate higher activity mid-year and on weekdays
        base = max(0, 5 - abs(week - 26)) * 2
        weekday_bonus = 3 if day < 5 else 0
        val = max(0, base + weekday_bonus + random.randint(-3, 5))
        cal_data.append(val)

heatmap = CalendarHeatmap(
    data=cal_data, rows=7, cols=52,
    x=100, y=180, cell_size=16, gap=3,
    colormap=['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353'],
    creation=9.0,
)
heatmap.fadein(9.2, 10.0)
heatmap.fadeout(11.5, 12.0)
show.add(heatmap)

# Day labels
day_names = ['Mon', '', 'Wed', '', 'Fri', '', '']
for i, name in enumerate(day_names):
    if not name:
        continue
    dlbl = Text(
        text=name, x=75, y=195 + i * 19, font_size=12,
        fill='#555', stroke_width=0, text_anchor='end', creation=9.0,
    )
    dlbl.fadein(9.3, 9.8)
    dlbl.fadeout(11.5, 12.0)
    show.add(dlbl)

# Color legend
legend_label = Text(
    text='Less', x=700, y=360, font_size=13,
    fill='#555', stroke_width=0, text_anchor='end', creation=9.0,
)
legend_label.fadein(9.5, 10.0)
legend_label.fadeout(11.5, 12.0)
show.add(legend_label)

legend_colors = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
for j, lc in enumerate(legend_colors):
    swatch = Rectangle(
        width=14, height=14, x=710 + j * 18, y=350,
        fill=lc, fill_opacity=1, stroke_width=0, creation=9.0,
    )
    swatch.fadein(9.5, 10.0)
    swatch.fadeout(11.5, 12.0)
    show.add(swatch)

legend_more = Text(
    text='More', x=810, y=360, font_size=13,
    fill='#555', stroke_width=0, text_anchor='start', creation=9.0,
)
legend_more.fadein(9.5, 10.0)
legend_more.fadeout(11.5, 12.0)
show.add(legend_more)

# Stats summary below
stats_text = Text(
    text=f'{sum(cal_data):,} contributions in the last year',
    x=960, y=440, font_size=26, fill='#ccc', stroke_width=0,
    text_anchor='middle', creation=9.0,
)
stats_text.fadein(9.8, 10.3)
stats_text.fadeout(11.5, 12.0)
show.add(stats_text)

# =============================================================================
# Phase 5 (12-15s): Scoreboard metrics panel
# =============================================================================
score_title = Text(
    text='Team Scoreboard', x=960, y=70, font_size=42,
    fill='#fff', stroke_width=0, text_anchor='middle', creation=12.0,
)
score_title.fadein(12.0, 12.5)
score_title.fadeout(14.5, 15.0)
show.add(score_title)

scoreboard = Scoreboard(
    entries=[
        ('Goals', '127'),
        ('Assists', '84'),
        ('Wins', '31'),
        ('Losses', '9'),
    ],
    x=260, y=180, col_width=350, row_height=100,
    bg_color='#12122a', font_size=48,
    creation=12.0,
)
scoreboard.fadein(12.2, 12.8)
scoreboard.fadeout(14.5, 15.0)
show.add(scoreboard)

# Second scoreboard row with different metrics
scoreboard2 = Scoreboard(
    entries=[
        ('Clean Sheets', '18'),
        ('Pass Accuracy', '89%'),
        ('Possession', '62%'),
        ('Shots on Target', '245'),
    ],
    x=260, y=320, col_width=350, row_height=100,
    bg_color='#12122a', font_size=48,
    creation=12.0,
)
scoreboard2.fadein(12.4, 13.0)
scoreboard2.fadeout(14.5, 15.0)
show.add(scoreboard2)

# Season label
season_lbl = Text(
    text='2025-26 Season Statistics', x=960, y=520, font_size=24,
    fill='#666', stroke_width=0, text_anchor='middle', creation=12.0,
)
season_lbl.fadein(12.5, 13.0)
season_lbl.fadeout(14.5, 15.0)
show.add(season_lbl)

# Decorative sparklines showing form guide
form_data = [1, 3, 3, 1, 3, 0, 3, 1, 3, 3, 3, 1, 0, 3, 3, 1, 3, 3, 0, 3]
form_spark = SparkLine(
    data=form_data, x=560, y=570, width=800, height=50,
    stroke='#4ECDC4', stroke_width=2, show_endpoint=True,
    creation=12.0,
)
form_spark.fadein(12.6, 13.2)
form_spark.fadeout(14.5, 15.0)
show.add(form_spark)

form_label = Text(
    text='Recent Form (points per game)', x=960, y=650, font_size=18,
    fill='#555', stroke_width=0, text_anchor='middle', creation=12.0,
)
form_label.fadein(12.6, 13.2)
form_label.fadeout(14.5, 15.0)
show.add(form_label)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    show.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
