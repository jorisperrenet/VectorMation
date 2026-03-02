import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/venn_org')
canvas.set_background()

title = Text(text='Moving Label, Spans, Venn & Org Chart', x=960, y=50,
             font_size=36, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Axes with moving label + spans ---
ax = Axes(x_range=(0, 10), y_range=(0, 10),
          plot_width=350, plot_height=250,
          x=50, y=120)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

curve = ax.plot(lambda x: 2 + 3 * (x / 10) ** 2 * 8, stroke='#FF79C6')
curve.create(1.5, 2.5)

# Vertical span highlighting a region
vspan = ax.add_vertical_span(3, 6, fill='#58C4DD', fill_opacity=0.1)
vspan.fadein(2, 2.5)

# Horizontal span
hspan = ax.add_horizontal_span(4, 7, fill='#83C167', fill_opacity=0.1)
hspan.fadein(2.2, 2.7)

# Moving label tracking the curve
ml = ax.add_moving_label(curve, 'Value', x_start=1, x_end=9, start=2, end=5)

ax_label = Text(text='Moving Label + Spans', x=225, y=110,
                font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
ax_label.fadein(1, 1.5)

# --- Venn Diagram (2 circles) ---
venn2 = VennDiagram(['Python', 'JavaScript'], x=700, y=280, radius=120)
venn2.fadein(1, 2)

venn2_label = Text(text='Venn Diagram (2)', x=700, y=120,
                   font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
venn2_label.fadein(1, 1.5)

# --- Venn Diagram (3 circles) ---
venn3 = VennDiagram(['Design', 'Code', 'Data'], x=1100, y=280, radius=100,
                    colors=['#FF79C6', '#58C4DD', '#83C167'])
venn3.fadein(1.5, 2.5)

venn3_label = Text(text='Venn Diagram (3)', x=1100, y=120,
                   font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
venn3_label.fadein(1, 1.5)

# --- Org Chart ---
org = ('CEO', [
    ('CTO', [
        ('Frontend', []),
        ('Backend', []),
        ('DevOps', []),
    ]),
    ('CFO', [
        ('Accounting', []),
        ('Finance', []),
    ]),
    ('COO', [
        ('Operations', []),
        ('HR', []),
    ]),
])
chart = OrgChart(org, x=960, y=550, h_spacing=160, v_spacing=90,
                 box_width=110, box_height=35)
chart.fadein(2, 3)

org_label = Text(text='Organization Chart', x=960, y=520,
                 font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
org_label.fadein(1, 1.5)

canvas.add_objects(ax, title, curve, vspan, hspan, ml,
                   venn2, venn3, chart,
                   ax_label, venn2_label, venn3_label, org_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/venn_org_example.mp4', fps=30, end=5)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
