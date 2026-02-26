import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/funnel_gauge')
canvas.set_background()

title = Text(text='Funnel, TreeMap, Gauge & SparkLine', x=960, y=50,
             font_size=36, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Funnel chart ---
stages = [('Visitors', 10000), ('Leads', 4200), ('Qualified', 1800),
          ('Proposals', 700), ('Closed', 250)]
funnel = FunnelChart(stages, x=50, y=120, width=500, height=400, gap=5)
funnel.fadein(1, 2)

funnel_label = Text(text='Funnel Chart', x=300, y=110,
                    font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
funnel_label.fadein(1, 1.5)

# --- TreeMap ---
tree_data = [('Engineering', 45), ('Marketing', 25), ('Sales', 20),
             ('Support', 15), ('HR', 10), ('Legal', 8), ('Ops', 5)]
treemap = TreeMap(tree_data, x=620, y=120, width=650, height=400)
treemap.fadein(1.5, 2.5)

treemap_label = Text(text='TreeMap', x=945, y=110,
                     font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
treemap_label.fadein(1, 1.5)

# --- Gauge chart ---
gauge = GaugeChart(72, min_val=0, max_val=100, x=300, y=780,
                   radius=150, label='Performance')
gauge.fadein(2, 3)

gauge_label = Text(text='Gauge Chart', x=300, y=580,
                   font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
gauge_label.fadein(1, 1.5)

# --- SparkLines ---
spark1 = SparkLine([3, 7, 2, 8, 5, 9, 4, 6], x=700, y=600, width=200, height=40,
                   stroke='#58C4DD', show_endpoint=True)
spark1.fadein(2, 2.5)

spark2 = SparkLine([10, 8, 12, 6, 14, 9, 11], x=700, y=660, width=200, height=40,
                   stroke='#83C167', show_endpoint=True)
spark2.fadein(2.2, 2.7)

spark3 = SparkLine([5, 3, 7, 2, 6, 1, 8, 4], x=700, y=720, width=200, height=40,
                   stroke='#FF6B6B', show_endpoint=True)
spark3.fadein(2.4, 2.9)

spark_label = Text(text='SparkLines', x=800, y=580,
                   font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
spark_label.fadein(1, 1.5)

# SparkLine labels
for i, (name, color) in enumerate([('Revenue', '#58C4DD'), ('Users', '#83C167'), ('Errors', '#FF6B6B')]):
    lbl = Text(text=name, x=690, y=620 + i * 60, font_size=14, fill=color,
               stroke_width=0, text_anchor='end')
    lbl.fadein(2 + i * 0.2, 2.5 + i * 0.2)
    canvas.add_objects(lbl)

canvas.add_objects(title, funnel, treemap, gauge,
                   spark1, spark2, spark3,
                   funnel_label, treemap_label, gauge_label, spark_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
