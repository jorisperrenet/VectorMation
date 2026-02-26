import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/waffle_mindmap')
canvas.set_background()

title = Text(text='Density, Annotation Box, Waffle & Mind Map', x=960, y=40,
             font_size=32, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Density plot ---
import random
random.seed(42)
ax = Axes(x_range=(-4, 4), y_range=(0, 0.5),
          plot_width=350, plot_height=200, x=50, y=100)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

data = [random.gauss(0, 1) for _ in range(100)]
kde = ax.plot_density(data, stroke='#FF79C6', stroke_width=2)
kde.fadein(1.5, 2.5)

# Annotation box
ab = ax.add_annotation_box(0, 0.4, 'Peak', offset=(80, -40))
ab.fadein(2, 2.5)

density_label = Text(text='Density Plot + Annotation', x=225, y=90,
                     font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
density_label.fadein(1, 1.5)

# --- Waffle Chart ---
cats = [('Product A', 45, '#58C4DD'), ('Product B', 30, '#83C167'),
        ('Product C', 15, '#FF6B6B'), ('Other', 10, '#FFFF00')]
waffle = WaffleChart(cats, x=550, y=100, grid_size=10, cell_size=18, gap=2)
waffle.fadein(1, 2)

waffle_label = Text(text='Waffle Chart', x=700, y=85,
                    font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
waffle_label.fadein(1, 1.5)

# --- Mind Map ---
root = ('Project', [
    ('Design', [('UI', []), ('UX', []), ('Brand', [])]),
    ('Engineering', [('Frontend', []), ('Backend', []), ('DevOps', [])]),
    ('Marketing', [('SEO', []), ('Content', [])]),
    ('Sales', [('Enterprise', []), ('SMB', [])]),
])
mm = MindMap(root, cx=700, cy=700, radius=200, font_size=15)
mm.fadein(2, 3)

mm_label = Text(text='Mind Map', x=700, y=450,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
mm_label.fadein(1, 1.5)

canvas.add_objects(title, ax, kde, ab, density_label,
                   waffle, waffle_label, mm, mm_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
