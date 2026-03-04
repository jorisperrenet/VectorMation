"""Colliding Blocks — recreation of 3b1b's 'Why do colliding blocks compute pi?'

A small block sliding into a larger block against a wall. The number of
collisions encodes digits of pi when the mass ratio is a power of 100.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/colliding_blocks')
canvas.set_background()

# ── Parameters ────────────────────────────────────────────────────────
mass_ratio = 100  # 100^1 → 31 collisions (starts digits of pi: 3.1...)
m1 = 1            # small block
m2 = mass_ratio   # large block
v1, v2 = 0, -300  # initial velocities in px/s (large block moves left)

# ── Simulate collisions ──────────────────────────────────────────────
x1, x2 = 600.0, 1200.0  # initial SVG x positions (block centers)
block_w1 = 80
block_w2 = 100
wall_x = 200.0

dt = 0.0001
T = 8.0
n_steps = int(T / dt)
collision_count = 0

collision_times = []  # (time, cumulative_count)
traj_x1, traj_x2 = [x1], [x2]
for step in range(n_steps):
    x1 += v1 * dt
    x2 += v2 * dt
    # Block-block collision (right edge of small meets left edge of big)
    if x2 - block_w2 <= x1 + block_w1:
        new_v1 = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
        new_v2 = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)
        v1, v2 = new_v1, new_v2
        x2 = x1 + block_w1 + block_w2
        collision_count += 1
        collision_times.append(((step + 1) * dt, collision_count))
    # Wall collision (left edge of small meets wall)
    if x1 - block_w1 <= wall_x:
        v1 = -v1
        x1 = wall_x + block_w1
        collision_count += 1
        collision_times.append(((step + 1) * dt, collision_count))
    traj_x1.append(x1)
    traj_x2.append(x2)

# ── Ground and wall ──────────────────────────────────────────────────
ground = Line(x1=100, y1=700, x2=1820, y2=700,
              stroke='#555', stroke_width=3, creation=0)
wall = Line(x1=wall_x, y1=300, x2=wall_x, y2=700,
            stroke='#888', stroke_width=5, creation=0)

# ── Blocks ────────────────────────────────────────────────────────────
small_h = block_w1 * 2
big_h = block_w2 * 2
small_block = Rectangle(width=block_w1 * 2, height=small_h,
                        x=traj_x1[0] - block_w1, y=700 - small_h,
                        fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD',
                        stroke_width=2, creation=0)
big_block = Rectangle(width=block_w2 * 2, height=big_h,
                      x=traj_x2[0] - block_w2, y=700 - big_h,
                      fill='#FC6255', fill_opacity=0.8, stroke='#FC6255',
                      stroke_width=2, creation=0)

# Animate block positions from precomputed trajectories
sample_rate = 60  # keyframes per second
frame_skip = max(1, int(1 / (dt * sample_rate)))

prev_t = 0
for i in range(frame_skip, len(traj_x1), frame_skip):
    t = i * dt
    small_block.x.set(prev_t, t, traj_x1[i] - block_w1)
    big_block.x.set(prev_t, t, traj_x2[i] - block_w2)
    prev_t = t

# ── Labels (follow blocks) ────────────────────────────────────────────
m1_label = TexObject('1 kg', x=traj_x1[0], y=700 - small_h - 50,
                     font_size=28, fill='#fff', stroke_width=0, anchor='center',
                     creation=0)
m2_label = TexObject('100 kg', x=traj_x2[0],
                     y=700 - big_h - 50, font_size=28, fill='#fff',
                     stroke_width=0, anchor='center', creation=0)

prev_t = 0
for i in range(frame_skip, len(traj_x1), frame_skip):
    t = i * dt
    m1_label.x.set(prev_t, t, traj_x1[i])
    m2_label.x.set(prev_t, t, traj_x2[i])
    prev_t = t

# ── Title + collision counter ─────────────────────────────────────────
title = TexObject(r'Colliding Blocks Compute $\pi$', x=960, y=60,
                  font_size=42, fill='#fff', stroke_width=0, anchor='center',
                  creation=0)
title.fadein(0, 1)

counter = TexCountAnimation(start_val=0, end_val=0, start=0, end=0,
                            fmt='Collisions: {:.0f}', x=960, y=160,
                            font_size=28, fill='#83C167', stroke_width=0,
                            text_anchor='middle', creation=0)
counter.fadein(0.5, 1.5)
for col_t, col_count in collision_times:
    counter.count_to(col_count, col_t, col_t + 0.01)

ratio_text = TexObject(rf'$\text{{Mass ratio}} = {mass_ratio}:1$', x=960, y=180,
                       font_size=22, fill='#aaa', stroke_width=0,
                       anchor='center', creation=0)
ratio_text.fadein(0.5, 1.5)

pi_text = TexObject(r'$\pi \approx 3.1415$', x=960, y=220,
                    font_size=22, fill='#FFFF00', stroke_width=0,
                    anchor='center', creation=0)
pi_text.fadein(1, 2)

canvas.add(ground, wall, small_block, big_block, m1_label, m2_label,
           title, counter, ratio_text, pi_text)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/colliding_blocks.mp4', fps=30, end=8)
if not args.for_docs:
    canvas.browser_display(start=args.start or 0, end=args.end or 8,
    fps=args.fps, port=args.port)
