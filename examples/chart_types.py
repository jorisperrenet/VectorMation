import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import random
random.seed(42)
args = parse_args()

COLS = 4
ROW_H = 280
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 5
COLORS = ['#58C4DD', '#83C167', '#FC6255', '#F0AC5F', '#9A72AC', '#5CD0B3']

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/chart_types')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 60

title = Text(text='Chart Types', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

# ── Row 0 ──────────────────────────────────────────────────────────────

# (0,0) GaugeChart
lbl = Text(text='GaugeChart', x=col_x(0), y=lbl_y(0), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = GaugeChart(value=72, min_val=0, max_val=100,
                 x=col_x(0), y=obj_y(0) + 50, radius=80, font_size=18)
objs += [lbl, obj]

# (0,1) SparkLine
lbl = Text(text='SparkLine', x=col_x(1), y=lbl_y(0), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
spark_data = [random.randint(10, 90) for _ in range(30)]
obj = SparkLine(data=spark_data, x=col_x(1) - 100, y=obj_y(0) + 30,
                width=200, height=80, stroke='#58C4DD', stroke_width=2,
                show_endpoint=True)
objs += [lbl, obj]

# (0,2) DonutChart
lbl = Text(text='DonutChart', x=col_x(2), y=lbl_y(0), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = DonutChart(values=[35, 25, 20, 15, 5],
                 labels=['A', 'B', 'C', 'D', 'E'],
                 cx=col_x(2), cy=obj_y(0) + 60, r=90, inner_radius=50,
                 font_size=12)
objs += [lbl, obj]

# (0,3) FunnelChart
lbl = Text(text='FunnelChart', x=col_x(3), y=lbl_y(0), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = FunnelChart(stages=[('Visits', 1000), ('Leads', 600), ('Trials', 300), ('Sales', 120)],
                  x=col_x(3) - 150, y=obj_y(0) - 10,
                  width=300, height=200, font_size=13)
objs += [lbl, obj]

# ── Row 1 ──────────────────────────────────────────────────────────────

# (1,0) TreeMap
lbl = Text(text='TreeMap', x=col_x(0), y=lbl_y(1), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = TreeMap(data=[('Alpha', 40), ('Beta', 30), ('Gamma', 20), ('Delta', 15),
                    ('Eps', 10), ('Zeta', 8)],
              x=col_x(0) - 150, y=obj_y(1) - 10, width=300, height=180,
              font_size=12)
objs += [lbl, obj]

# (1,1) WaffleChart
lbl = Text(text='WaffleChart', x=col_x(1), y=lbl_y(1), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = WaffleChart(categories=[('Yes', 62, '#83C167'), ('No', 28, '#FC6255'),
                               ('Maybe', 10, '#F0AC5F')],
                  x=col_x(1) - 90, y=obj_y(1) - 10, grid_size=8,
                  cell_size=14, gap=2, font_size=11)
objs += [lbl, obj]

# (1,2) BulletChart
lbl = Text(text='BulletChart', x=col_x(2), y=lbl_y(2 - 1), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = BulletChart(actual=75, target=90,
                  ranges=[(60, '#2a2a3a'), (80, '#3a3a4a'), (100, '#4a4a5a')],
                  label='Revenue',
                  x=col_x(2) - 100, y=obj_y(1) + 50, width=250, height=35,
                  font_size=13)
objs += [lbl, obj]

# (1,3) SankeyDiagram
lbl = Text(text='SankeyDiagram', x=col_x(3), y=lbl_y(1), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = SankeyDiagram(flows=[('A', 'X', 30), ('A', 'Y', 20), ('B', 'X', 15),
                           ('B', 'Y', 25), ('B', 'Z', 10)],
                    x=col_x(3) - 120, y=obj_y(1), width=240, height=150,
                    node_width=12, font_size=10)
objs += [lbl, obj]

# ── Row 2 ──────────────────────────────────────────────────────────────

# (2,0) WaterfallChart
lbl = Text(text='WaterfallChart', x=col_x(0), y=lbl_y(2), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = WaterfallChart(values=[50, 30, -15, 20, -10],
                     labels=['Q1', 'Q2', 'Q3', 'Q4', 'Adj', 'Net'],
                     x=col_x(0) - 160, y=obj_y(2) - 20, width=320, height=200,
                     font_size=11)
objs += [lbl, obj]

# (2,1) GanttChart
lbl = Text(text='GanttChart', x=col_x(1), y=lbl_y(2), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = GanttChart(tasks=[('Design', 0, 3), ('Dev', 2, 7), ('Test', 6, 9), ('Launch', 8, 10)],
                 x=col_x(1) - 180, y=obj_y(2) - 10, width=360,
                 bar_height=22, bar_spacing=8, font_size=11)
objs += [lbl, obj]

# (2,2) CalendarHeatmap
lbl = Text(text='CalendarHeatmap', x=col_x(2), y=lbl_y(2), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
cal_data = [random.randint(0, 10) for _ in range(7 * 26)]
obj = CalendarHeatmap(data=cal_data, rows=7, cols=26,
                      x=col_x(2) - 130, y=obj_y(2) - 5,
                      cell_size=8, gap=2)
objs += [lbl, obj]

# (2,3) MatrixHeatmap
lbl = Text(text='MatrixHeatmap', x=col_x(3), y=lbl_y(2), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
matrix_data = [[random.uniform(0, 10) for _ in range(5)] for _ in range(5)]
obj = MatrixHeatmap(data=matrix_data,
                    row_labels=['R1', 'R2', 'R3', 'R4', 'R5'],
                    col_labels=['C1', 'C2', 'C3', 'C4', 'C5'],
                    x=col_x(3) - 110, y=obj_y(2) - 10, cell_size=30, gap=2,
                    font_size=10)
objs += [lbl, obj]

# ── Row 3 ──────────────────────────────────────────────────────────────

# (3,0) Scoreboard
lbl = Text(text='Scoreboard', x=col_x(0), y=lbl_y(3), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = Scoreboard(entries=[('Users', '12.4k'), ('Revenue', '$84k'),
                          ('Growth', '+18%'), ('NPS', '72')],
                 x=col_x(0) - 150, y=obj_y(3) - 10, col_width=150, row_height=50,
                 font_size=20, cols=2)
objs += [lbl, obj]

# (3,1) KPICard
lbl = Text(text='KPICard', x=col_x(1), y=lbl_y(3), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
kpi_trend = [random.randint(40, 100) for _ in range(15)]
obj = KPICard(title='Monthly Revenue', value='$84.2k', subtitle='+12% vs prev',
              trend_data=kpi_trend,
              x=col_x(1) - 130, y=obj_y(3) - 10, width=260, height=150,
              font_size=36)
objs += [lbl, obj]

# (3,2) SampleSpace
lbl = Text(text='SampleSpace', x=col_x(2), y=lbl_y(3), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = SampleSpace(width=280, height=170, x=col_x(2) - 140, y=obj_y(3) - 10)
obj.divide_horizontally(0.6, colors=('#58C4DD', '#FC6255'), labels=['P(A)=0.6', 'P(B)=0.4'])
objs += [lbl, obj]

# (3,3) TimelineBar
lbl = Text(text='TimelineBar', x=col_x(3), y=lbl_y(3), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = TimelineBar(markers={0: 'Start', 3: 'Alpha', 6: 'Beta', 8: 'RC', 10: 'Release'},
                  total_duration=10,
                  x=col_x(3) - 170, y=obj_y(3) + 60, width=340, height=5,
                  font_size=11)
objs += [lbl, obj]

# ── Row 4 ──────────────────────────────────────────────────────────────

# (4,0) RadarChart
lbl = Text(text='RadarChart', x=col_x(0), y=lbl_y(4), font_size=20, fill='#999',
           stroke_width=0, text_anchor='middle')
obj = RadarChart(
    values=[85, 70, 90, 60, 95, 75],
    labels=['Spd', 'Pow', 'Acc', 'Def', 'Sta', 'Agi'],
    max_val=100, cx=col_x(0), cy=obj_y(4) + 60, radius=80, font_size=10,
)
objs += [lbl, obj]

canvas.add_objects(*objs)

if args.for_docs:
    canvas.write_frame(filename='docs/source/_static/videos/chart_types.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
