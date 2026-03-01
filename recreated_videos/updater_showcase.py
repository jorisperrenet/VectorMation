"""Showcase of add_updater, ValueTracker, and dynamic behaviors."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import math
from vectormation.objects import (
    VectorMathAnim, Text, ORIGIN, parse_args,
    Circle, Dot, Line, Rectangle, ValueTracker,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/updater_showcase')

# Title
title = Text(text='Updaters & Dynamic Behaviors', x=ORIGIN[0], y=50,
             font_size=40, fill='#58C4DD', text_anchor='middle')
title.write(0, 0.8)
canvas.add(title)

# ── Section 1: Dot following a circle path via updater ──────────────────
label1 = Text(text='Updater: Dot on Circle', x=480, y=110,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label1)

orbit_circle = Circle(r=150, cx=480, cy=320, fill_opacity=0,
                      stroke='#444', stroke_width=1, creation=0.5)
canvas.add(orbit_circle)

orbit_dot = Dot(cx=630, cy=320, r=12, fill='#FF6B6B', creation=0.5)

def orbit_updater(obj, t):
    angle = t * math.pi * 0.8
    obj.c.set_onward(t, (480 + 150 * math.cos(angle),
                         320 + 150 * math.sin(angle)))

orbit_dot.add_updater(orbit_updater, start=0, end=8)
canvas.add(orbit_dot)

# Trail effect using trace_path
trail = orbit_dot.trace_path(start=0.5, end=8, stroke='#FF6B6B',
                             stroke_width=2, stroke_opacity=0.5)
canvas.add(trail)

# ── Section 2: ValueTracker driving a progress display ──────────────────
label2 = Text(text='ValueTracker Progress', x=1440, y=110,
              font_size=22, fill='#aaa', text_anchor='middle', creation=0.5)
canvas.add(label2)

tracker = ValueTracker(0)
tracker.animate_value(100, start=0, end=4)
tracker.set_value(100, start=4)
tracker.animate_value(0, start=5, end=8)

# Progress bar driven by tracker
bar_bg = Rectangle(width=400, height=30, x=1240, y=250,
                   fill='#333', fill_opacity=0.8, stroke='#666', creation=0.5)
canvas.add(bar_bg)

bar_fill = Rectangle(width=1, height=30, x=1240, y=250,
                     fill='#83C167', fill_opacity=1, stroke_width=0, creation=0.5)

def bar_updater(obj, t):
    val = tracker.at_time(t) / 100
    obj.width.set_onward(t, max(1, 400 * val))

bar_fill.add_updater(bar_updater, start=0, end=8)
canvas.add(bar_fill)

pct_text = Text(text='0%', x=1440, y=305, font_size=28, fill='#fff',
                text_anchor='middle', creation=0.5)

def pct_updater(obj, t):
    val = tracker.at_time(t)
    obj.set_text(f'{val:.0f}%', start=t)

pct_text.add_updater(pct_updater, start=0, end=8)
canvas.add(pct_text)

# ── Section 3: Always-rotating shapes ───────────────────────────────────
label3 = Text(text='always_rotate + always_shift', x=480, y=510,
              font_size=22, fill='#aaa', text_anchor='middle', creation=1)
canvas.add(label3)

# Rotating rectangle
rot_rect = Rectangle(width=80, height=40, x=380, y=630,
                     fill='#58C4DD', fill_opacity=0.7, creation=1)
rot_rect.always_rotate(degrees_per_second=90, start=1, end=8)
canvas.add(rot_rect)

# Bouncing dot
bounce_dot = Dot(cx=580, cy=700, r=10, fill='#FFFF00', creation=1)
bounce_dot.always_shift(vx=80, vy=0, start=1, end=4)
bounce_dot.always_shift(vx=-80, vy=0, start=4, end=7)
canvas.add(bounce_dot)

# ── Section 4: Connected elements ───────────────────────────────────────
label4 = Text(text='Dynamic Connections', x=1440, y=510,
              font_size=22, fill='#aaa', text_anchor='middle', creation=2)
canvas.add(label4)

# Two dots connected by a line that follows them
dot_a = Dot(cx=1300, cy=650, r=10, fill='#FF6B6B', creation=2)
dot_b = Dot(cx=1580, cy=750, r=10, fill='#83C167', creation=2)

dot_a.shift(dx=0, dy=-150, start=2, end=4)
dot_a.shift(dx=0, dy=150, start=4, end=6)
dot_b.shift(dx=-100, dy=-100, start=3, end=5)
dot_b.shift(dx=100, dy=100, start=5, end=7)

canvas.add(dot_a)
canvas.add(dot_b)

connector = Line(x1=1300, y1=650, x2=1580, y2=750,
                 stroke='#666', stroke_width=2, stroke_dasharray='6 4',
                 creation=2)

def connect_updater(obj, t):
    ax, ay = dot_a.center(t)
    bx, by = dot_b.center(t)
    obj.p1.set_onward(t, (ax, ay))
    obj.p2.set_onward(t, (bx, by))

connector.add_updater(connect_updater, start=2, end=8)
canvas.add(connector)

# Midpoint label
mid_label = Text(text='d=?', x=1440, y=700, font_size=18,
                 fill='#aaa', text_anchor='middle', creation=2)

def mid_updater(obj, t):
    ax, ay = dot_a.center(t)
    bx, by = dot_b.center(t)
    dist = math.hypot(bx - ax, by - ay)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    obj.set_text(f'd={dist:.0f}', start=t)
    obj.x.set_onward(t, mx)
    obj.y.set_onward(t, my - 15)

mid_label.add_updater(mid_updater, start=2, end=8)
canvas.add(mid_label)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 8,
                           fps=args.fps, port=args.port)
