"""Sankey diagrams, funnel charts, and flow visualizations demo."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    SankeyDiagram, FunnelChart, WaterfallChart,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/sankey_flows')

# Title
title = Text(text='Flow & Process Visualizations', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Sankey Diagram: Energy Flow ──────────────────────────────────────
label1 = Text(text='Sankey — Energy Flow', x=ORIGIN[0], y=110,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

sankey = SankeyDiagram(
    flows=[
        ('Solar', 'Grid', 40),
        ('Solar', 'Battery', 20),
        ('Wind', 'Grid', 35),
        ('Wind', 'Export', 10),
        ('Gas', 'Grid', 25),
        ('Grid', 'Homes', 60),
        ('Grid', 'Industry', 30),
        ('Grid', 'Transport', 10),
        ('Battery', 'Homes', 15),
        ('Battery', 'Transport', 5),
    ],
    x=160, y=140, width=1600, height=420,
    creation=1.0
)
sankey.stagger('fadein', start=1.0, end=3.0)
canvas.add(sankey)

# ── Funnel Chart: Sales Pipeline ─────────────────────────────────────
label2 = Text(text='Funnel — Sales Pipeline', x=480, y=620,
              font_size=22, fill='#aaa', text_anchor='middle', creation=4)
canvas.add(label2)

funnel = FunnelChart(
    stages=[
        ('Leads', 1000),
        ('Qualified', 600),
        ('Proposals', 300),
        ('Negotiations', 150),
        ('Won', 80),
    ],
    x=180, y=660, width=600, height=380,
    creation=4
)
funnel.stagger('fadein', start=4.5, end=6)
canvas.add(funnel)

# ── Waterfall Chart: Budget ──────────────────────────────────────────
label3 = Text(text='Waterfall — Quarterly Budget', x=1440, y=620,
              font_size=22, fill='#aaa', text_anchor='middle', creation=4)
canvas.add(label3)

waterfall = WaterfallChart(
    values=[500, -200, 300, -120, -45, 135],
    labels=['Revenue', 'COGS', 'Gross', 'OpEx', 'Tax', 'Net'],
    x=1090, y=660, width=700, height=380,
    creation=4
)
waterfall.stagger('fadein', start=4.5, end=6)
canvas.add(waterfall)

canvas.browser_display(start=args.start or 0, end=args.end or 7,
                           fps=args.fps, port=args.port)
