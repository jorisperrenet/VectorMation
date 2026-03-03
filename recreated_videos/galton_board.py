"""Galton Board simulation -- balls bounce through pegs into buckets,
forming a binomial/normal distribution.

Inspired by 3Blue1Brown's Central Limit Theorem video (2023).
"""
import math
import random
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vectormation.objects import *

random.seed(42)

# --- Configuration ---
N_ROWS = 7
N_PEGS_ROW = 11
SPACING = 90  # px between pegs
PEG_RADIUS = 8
BALL_RADIUS = 10
TOP_Y = 120
N_BALLS = 60

v = VectorMathAnim(save_dir='svgs/galton_board')
v.set_background(fill='#1a1a2e')

# --- Build pegs ---
pegs = VCollection(creation=0)
peg_positions = []  # row -> list of (cx, cy)

center_x = CANVAS_WIDTH / 2
for row in range(N_ROWS):
    row_pegs = []
    n_in_row = N_PEGS_ROW - (row % 2)
    offset_x = center_x - (n_in_row - 1) * SPACING / 2 + (row % 2) * SPACING / 2
    cy = TOP_Y + row * SPACING * math.sqrt(3) / 2
    for i in range(n_in_row):
        cx = offset_x + i * SPACING
        peg = Dot(r=PEG_RADIUS, cx=cx, cy=cy, fill='#888',
                  fill_opacity=1, stroke='#aaa', stroke_width=1, creation=0, z=0)
        pegs.add(peg)
        row_pegs.append((cx, cy))
    peg_positions.append(row_pegs)

pegs.stagger_fadein(start=0, end=1.5, shift_dir=DOWN)

# --- Build buckets ---
bucket_y_top = TOP_Y + N_ROWS * SPACING * math.sqrt(3) / 2 + SPACING * 0.6
bucket_height = CANVAS_HEIGHT - bucket_y_top - 40
bucket_width = SPACING * 0.8

# Bucket positions align with bottom row
bottom_row = peg_positions[-1]
# Add one extra bucket on each side
bucket_centers = []
for i in range(len(bottom_row) + 1):
    if i == 0:
        bx = bottom_row[0][0] - SPACING / 2
    elif i == len(bottom_row):
        bx = bottom_row[-1][0] + SPACING / 2
    else:
        bx = (bottom_row[i - 1][0] + bottom_row[i][0]) / 2
    bucket_centers.append(bx)

buckets = VCollection(creation=0)
for bx in bucket_centers:
    left_wall = Line(x1=bx - bucket_width / 2, y1=bucket_y_top,
                     x2=bx - bucket_width / 2, y2=bucket_y_top + bucket_height,
                     stroke='#555', stroke_width=2, creation=0)
    right_wall = Line(x1=bx + bucket_width / 2, y1=bucket_y_top,
                      x2=bx + bucket_width / 2, y2=bucket_y_top + bucket_height,
                      stroke='#555', stroke_width=2, creation=0)
    floor = Line(x1=bx - bucket_width / 2, y1=bucket_y_top + bucket_height,
                 x2=bx + bucket_width / 2, y2=bucket_y_top + bucket_height,
                 stroke='#555', stroke_width=2, creation=0)
    buckets.add(left_wall)
    buckets.add(right_wall)
    buckets.add(floor)

buckets.fadein(start=0.5, end=1.5)


# --- Simulate ball trajectories ---
def simulate_ball():
    """Simulate a ball bouncing through the peg grid.
    Returns list of (x, y, time_offset) waypoints."""
    x = center_x
    y = TOP_Y - 60  # start above pegs
    waypoints = [(x, y, 0)]
    t = 0
    fall_time = 0.15  # time to fall between rows

    for row in range(N_ROWS):
        # Find the nearest peg in this row
        row_pegs = peg_positions[row]
        # Ball goes left or right randomly
        direction = random.choice([-1, 1])
        # Find closest peg
        closest = min(row_pegs, key=lambda p: abs(p[0] - x))
        # Move to peg position + offset
        x = closest[0] + direction * SPACING / 2
        y = closest[1] + SPACING * math.sqrt(3) / 2 * 0.5
        t += fall_time
        waypoints.append((x, y, t))
        # Continue falling
        y = closest[1] + SPACING * math.sqrt(3) / 2
        t += fall_time * 0.5
        waypoints.append((x, y, t))

    # Fall into bucket
    # Find which bucket this ball lands in
    closest_bucket = min(range(len(bucket_centers)),
                         key=lambda i: abs(bucket_centers[i] - x))
    bx = bucket_centers[closest_bucket]
    t += fall_time
    waypoints.append((bx, bucket_y_top + 20, t))

    return waypoints, closest_bucket


# Count balls per bucket for stacking
bucket_counts = [0] * len(bucket_centers)

balls = []
ball_start = 2.0
ball_interval = 0.15

for i in range(N_BALLS):
    waypoints, bucket_idx = simulate_ball()
    ball_count = bucket_counts[bucket_idx]
    bucket_counts[bucket_idx] += 1

    # Final resting position: stacked in bucket
    bx = bucket_centers[bucket_idx]
    final_y = bucket_y_top + bucket_height - BALL_RADIUS - ball_count * BALL_RADIUS * 2

    start_t = ball_start + i * ball_interval
    total_fall = waypoints[-1][2]

    # Create the ball
    colors = ['#FFFF00', '#FFD700', '#FFA500', '#FF8C00', '#FF6347']
    color = colors[i % len(colors)]
    ball = Dot(r=BALL_RADIUS, cx=center_x, cy=TOP_Y - 60,
               fill=color, fill_opacity=0.9, stroke=lighten(color, 0.3),
               stroke_width=1, creation=start_t, z=1)

    # Animate through waypoints
    for j in range(len(waypoints) - 1):
        x0, y0, t0 = waypoints[j]
        x1, y1, t1 = waypoints[j + 1]
        t_start = start_t + t0
        t_end = start_t + t1
        if t_end > t_start:
            ball.c.set(t_start, t_end, lambda t, _s=t_start, _e=t_end, _x0=x0, _y0=y0, _x1=x1, _y1=y1:
                       (_x0 + (_x1 - _x0) * ((t - _s) / (_e - _s)),
                        _y0 + (_y1 - _y0) * ((t - _s) / (_e - _s))),
                       stay=False)

    # Settle into bucket
    settle_start = start_t + total_fall
    ball.c.set_onward(settle_start, (bx, final_y))

    balls.append(ball)

# --- Labels ---
title = Text(text='Galton Board', x=CANVAS_WIDTH / 2, y=50,
             font_size=42, text_anchor='middle', fill='#fff',
             stroke_width=0, creation=0)
title.fadein(start=0, end=1)

subtitle = Text(text='Central Limit Theorem', x=CANVAS_WIDTH / 2, y=85,
                font_size=24, text_anchor='middle', fill='#888',
                stroke_width=0, creation=0)
subtitle.fadein(start=0.5, end=1.5)

# Normal curve overlay (appears after balls settle)
curve_start = ball_start + N_BALLS * ball_interval + 2
mu = center_x
sigma = SPACING * math.sqrt(N_ROWS) / 2
curve_points = []
for i in range(200):
    x = mu - 4 * sigma + i * 8 * sigma / 199
    y_val = math.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))
    # Scale to fit bucket area
    y_screen = bucket_y_top + bucket_height - y_val * sigma * bucket_height * 2
    curve_points.append((x, y_screen))

normal_curve = Lines(*curve_points, stroke='#FF6B6B', stroke_width=3,
                     fill_opacity=0, creation=curve_start, z=2)
normal_curve.create(start=curve_start, end=curve_start + 2)

curve_label = Text(text='Normal Distribution', x=center_x + 250, y=bucket_y_top - 20,
                   font_size=20, text_anchor='start', fill='#FF6B6B',
                   stroke_width=0, creation=curve_start)
curve_label.fadein(start=curve_start, end=curve_start + 1)

# --- Add everything to canvas ---
v.add_objects(title, subtitle, buckets, pegs, *balls, normal_curve, curve_label)

# --- Run ---
args = parse_args()
total_time = curve_start + 3
    v.browser_display(start=0, end=total_time, fps=args.fps, port=args.port)
if args.output:
    v.export_video(args.output, start=0, end=curve_start + 3, fps=args.fps)
