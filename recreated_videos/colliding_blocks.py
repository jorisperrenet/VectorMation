"""Colliding Blocks — recreation of 3b1b's 'Why do colliding blocks compute pi?'

A small block sliding into a larger block against a wall. The number of
collisions encodes digits of pi when the mass ratio is a power of 100.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/colliding_blocks')
canvas.set_background()

# ── Parameters ────────────────────────────────────────────────────────
mass_ratio = 100  # 100^1 → 31 collisions (starts digits of pi: 3.1...)
m1 = 1            # small block
m2 = mass_ratio   # large block
v1, v2 = 0, -2    # initial velocities (large block moves left)

# ── Simulate collisions ──────────────────────────────────────────────
x1, x2 = 600.0, 1200.0  # initial SVG x positions
block_w = 80
wall_x = 200.0

dt = 0.0005
T = 8.0
n_steps = int(T / dt)
collision_count = 0

traj_x1, traj_x2 = [x1], [x2]
for _ in range(n_steps):
    x1 += v1 * dt
    x2 += v2 * dt
    # Block-block collision
    if x2 - block_w <= x1 + block_w:
        new_v1 = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
        new_v2 = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)
        v1, v2 = new_v1, new_v2
        x2 = x1 + 2 * block_w
        collision_count += 1
    # Wall collision
    if x1 - block_w <= wall_x:
        v1 = -v1
        x1 = wall_x + block_w
        collision_count += 1
    traj_x1.append(x1)
    traj_x2.append(x2)

# ── Ground and wall ──────────────────────────────────────────────────
ground = Line(x1=100, y1=700, x2=1820, y2=700,
              stroke='#555', stroke_width=3, creation=0)
wall = Line(x1=wall_x, y1=300, x2=wall_x, y2=700,
            stroke='#888', stroke_width=5, creation=0)

# ── Blocks ────────────────────────────────────────────────────────────
small_block = Rectangle(width=block_w * 2, height=block_w * 2,
                        x=traj_x1[0] - block_w, y=700 - block_w * 2,
                        fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD',
                        stroke_width=2, creation=0)
big_block = Rectangle(width=block_w * 2.5, height=block_w * 2.5,
                      x=traj_x2[0] - block_w, y=700 - block_w * 2.5,
                      fill='#FC6255', fill_opacity=0.8, stroke='#FC6255',
                      stroke_width=2, creation=0)

# Animate block positions from trajectories
fps_sim = 1 / dt
frame_skip = int(fps_sim / 60)  # sample every ~60fps

for i in range(0, len(traj_x1) - frame_skip, frame_skip):
    t = i * dt
    t_next = (i + frame_skip) * dt
    x1_now = traj_x1[i]
    x1_next = traj_x1[min(i + frame_skip, len(traj_x1) - 1)]
    dx1 = x1_next - x1_now
    if abs(dx1) > 0.1:
        small_block.shift(dx=dx1, dy=0, start=t, end=t_next)

    x2_now = traj_x2[i]
    x2_next = traj_x2[min(i + frame_skip, len(traj_x2) - 1)]
    dx2 = x2_next - x2_now
    if abs(dx2) > 0.1:
        big_block.shift(dx=dx2, dy=0, start=t, end=t_next)

# ── Labels ────────────────────────────────────────────────────────────
m1_label = Text(text=f'{m1} kg', x=traj_x1[0], y=700 - block_w - 10,
                font_size=20, fill='#fff', stroke_width=0, text_anchor='middle',
                creation=0)
m2_label = Text(text=f'{m2} kg', x=traj_x2[0] + block_w * 0.25,
                y=700 - block_w * 1.5, font_size=20, fill='#fff',
                stroke_width=0, text_anchor='middle', creation=0)

# ── Title + collision counter ─────────────────────────────────────────
title = Text(text='Colliding Blocks Compute Pi', x=960, y=60,
             font_size=42, fill='#fff', stroke_width=0, text_anchor='middle',
             creation=0)
title.fadein(0, 1)

counter = Text(text=f'Collisions: {collision_count}', x=960, y=120,
               font_size=28, fill='#83C167', stroke_width=0,
               text_anchor='middle', creation=0)
counter.fadein(0.5, 1.5)

ratio_text = Text(text=f'Mass ratio = {mass_ratio}:1', x=960, y=160,
                  font_size=22, fill='#aaa', stroke_width=0,
                  text_anchor='middle', creation=0)
ratio_text.fadein(0.5, 1.5)

pi_text = Text(text=f'π ≈ {math.pi:.4f}...', x=960, y=200,
               font_size=22, fill='#FFFF00', stroke_width=0,
               text_anchor='middle', creation=0)
pi_text.fadein(1, 2)

canvas.add(ground, wall, small_block, big_block, m1_label, m2_label,
           title, counter, ratio_text, pi_text)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 8,
                           fps=args.fps, port=args.port)
