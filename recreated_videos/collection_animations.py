"""VCollection animation methods: arrange, stagger, cascade, fan_out, etc."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import (
    VectorMathAnim, Circle, Rectangle, Text, Square, Dot, VCollection,
    ORIGIN, parse_args,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/collection_animations')

# Title
title = Text(text='VCollection Animations', x=ORIGIN[0], y=60,
             font_size=42, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Staggered Write ─────────────────────────────────────────────
label1 = Text(text='stagger + write', x=300, y=130, font_size=20,
              fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label1)

colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00', '#FF79C6']
circles = VCollection(*[Circle(r=30, fill=c, creation=0.5) for c in colors])
circles.arrange(direction=(1, 0), buff=20)
circles.center_to_pos(300, 230, start=0.5)
circles.stagger('write', delay=0.2, start=1, end=2)
canvas.add(circles)

# ── Cascade ─────────────────────────────────────────────────────
label2 = Text(text='cascade fadein', x=960, y=130, font_size=20,
              fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label2)

squares = VCollection(*[Square(50, fill=c, creation=0.5) for c in colors])
squares.arrange(direction=(1, 0), buff=15)
squares.center_to_pos(960, 230, start=0.5)
squares.stagger('fadein', delay=0.15, start=1, end=2)
canvas.add(squares)

# ── Fan Out ─────────────────────────────────────────────────────
label3 = Text(text='fan_out', x=1620, y=130, font_size=20,
              fill='#888', text_anchor='middle', creation=0.5)
canvas.add(label3)

dots = VCollection(*[Dot(r=15, fill=c, creation=0.5) for c in colors])
dots.center_to_pos(1620, 230, start=0.5)
dots.fan_out(cx=1620, cy=230, radius=80, start=1, end=2)
canvas.add(dots)

# ── Arrange in Grid ─────────────────────────────────────────────
label4 = Text(text='arrange_in_grid', x=300, y=350, font_size=20,
              fill='#888', text_anchor='middle', creation=3)
canvas.add(label4)

grid_items = VCollection(*[Square(45, fill=c, creation=3)
                            for c in colors * 2])
grid_items.arrange_in_grid(rows=2, cols=5, buff=10)
grid_items.center_to_pos(300, 460, start=3)
grid_items.stagger('fadein', delay=0.1, start=3.5, end=4.5)
canvas.add(grid_items)

# ── Wave Effect ─────────────────────────────────────────────────
label5 = Text(text='wave_anim', x=960, y=350, font_size=20,
              fill='#888', text_anchor='middle', creation=3)
canvas.add(label5)

wave_circles = VCollection(*[Circle(r=25, fill=c, creation=3) for c in colors])
wave_circles.arrange(direction=(1, 0), buff=20)
wave_circles.center_to_pos(960, 460, start=3)
wave_circles.stagger('fadein', delay=0.1, start=3.2, end=4)
wave_circles.wave_anim(start=4.5, end=6.5, amplitude=40, n_waves=2)
canvas.add(wave_circles)

# ── Set Color by Gradient ───────────────────────────────────────
label6 = Text(text='set_color_by_gradient', x=1620, y=350, font_size=20,
              fill='#888', text_anchor='middle', creation=3)
canvas.add(label6)

gradient_rects = VCollection(*[Rectangle(40, 60, creation=3) for _ in range(8)])
gradient_rects.arrange(direction=(1, 0), buff=8)
gradient_rects.center_to_pos(1620, 460, start=3)
gradient_rects.set_color_by_gradient('#FF0000', '#0000FF')
gradient_rects.stagger('fadein', delay=0.1, start=3.5, end=4.5)
canvas.add(gradient_rects)

# ── Waterfall ───────────────────────────────────────────────────
label7 = Text(text='waterfall', x=300, y=580, font_size=20,
              fill='#888', text_anchor='middle', creation=6)
canvas.add(label7)

wf_items = VCollection(*[Square(50, fill=c, creation=6) for c in colors])
wf_items.arrange(direction=(1, 0), buff=15)
wf_items.center_to_pos(300, 700, start=6)
wf_items.waterfall(start=6.5, end=7.5, height=120)
canvas.add(wf_items)

# ── Distribute ──────────────────────────────────────────────────
label8 = Text(text='distribute', x=960, y=580, font_size=20,
              fill='#888', text_anchor='middle', creation=6)
canvas.add(label8)

dist_items = VCollection(*[Circle(r=20, fill=c, creation=6) for c in colors])
dist_items.arrange(direction=(1, 0), buff=30)
dist_items.center_to_pos(960, 700, start=6)
dist_items.stagger('fadein', delay=0.15, start=6.5, end=7.5)
canvas.add(dist_items)

# ── Sequential ──────────────────────────────────────────────────
label9 = Text(text='sequential rotate', x=1620, y=580, font_size=20,
              fill='#888', text_anchor='middle', creation=6)
canvas.add(label9)

seq_items = VCollection(*[Rectangle(40, 60, fill=c, creation=6) for c in colors])
seq_items.arrange(direction=(1, 0), buff=15)
seq_items.center_to_pos(1620, 700, start=6)
seq_items.stagger('fadein', delay=0.1, start=6.3, end=7)
seq_items.sequential('rotate_by', start=7.5, end=9, degrees=180)
canvas.add(seq_items)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 9.5,
                           fps=args.fps, port=args.port)
