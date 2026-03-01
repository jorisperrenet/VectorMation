"""UI Components Demo — TextBox, Badge, Checklist, Stepper, SpeechBubble, Countdown."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/ui_components')
canvas.set_background()

T = 12.0

# Colors
WHITE = '#FFFFFF'
GREY = '#888888'
CYAN = '#58C4DD'
GREEN = '#83C167'
ORANGE = '#F5A623'
PINK = '#FF6B6B'
YELLOW = '#F5C542'

# =============================================================================
# Phase 1 (0-3s): Title + TextBox + Badges
# =============================================================================

# Title
title = Title('UI Components', creation=0)
title.fadein(0.0, 0.5)
title.fadeout(2.5, 3.0)
canvas.add(title)

# TextBox with a label
textbox = TextBox(
    'Username', x=300, y=300, font_size=22, padding=14,
    width=220, height=50, corner_radius=8,
    box_fill='#1e1e2e', box_opacity=0.95, text_color=WHITE,
)
textbox.fadein(0.3, 0.8)
textbox.fadeout(2.5, 3.0)
canvas.add(textbox)

textbox_label = Text(
    text='TextBox', x=410, y=280, font_size=16,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
textbox_label.fadein(0.3, 0.8)
textbox_label.fadeout(2.5, 3.0)
canvas.add(textbox_label)

# Badges
badge1 = Badge('v2.0', x=700, y=300, font_size=18, bg_color=CYAN, text_color='#000')
badge1.fadein(0.6, 1.0)
badge1.fadeout(2.5, 3.0)
canvas.add(badge1)

badge2 = Badge('NEW', x=830, y=300, font_size=18, bg_color=GREEN, text_color='#000')
badge2.fadein(0.8, 1.2)
badge2.fadeout(2.5, 3.0)
canvas.add(badge2)

badge3 = Badge('BETA', x=950, y=300, font_size=18, bg_color=ORANGE, text_color='#000')
badge3.fadein(1.0, 1.4)
badge3.fadeout(2.5, 3.0)
canvas.add(badge3)

badge_label = Text(
    text='Badge', x=880, y=280, font_size=16,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
badge_label.fadein(0.6, 1.0)
badge_label.fadeout(2.5, 3.0)
canvas.add(badge_label)

# Secondary TextBox below
textbox2 = TextBox(
    'Enter your email...', x=300, y=400, font_size=18, padding=12,
    width=280, height=44, corner_radius=6,
    box_fill='#262630', box_opacity=0.9, text_color='#666',
)
textbox2.fadein(0.5, 1.0)
textbox2.fadeout(2.5, 3.0)
canvas.add(textbox2)

# More badges in a row below
badge4 = Badge('STABLE', x=700, y=380, font_size=16, bg_color='#9B59B6', text_color=WHITE)
badge4.fadein(1.2, 1.6)
badge4.fadeout(2.5, 3.0)
canvas.add(badge4)

badge5 = Badge('DOCS', x=850, y=380, font_size=16, bg_color='#555', text_color=WHITE)
badge5.fadein(1.4, 1.8)
badge5.fadeout(2.5, 3.0)
canvas.add(badge5)

# =============================================================================
# Phase 2 (3-6s): Checklist + Stepper
# =============================================================================

phase2_label = Text(
    text='Checklist & Stepper', x=960, y=180, font_size=36,
    fill=WHITE, stroke_width=0, text_anchor='middle',
)
phase2_label.fadein(3.0, 3.4)
phase2_label.fadeout(5.5, 6.0)
canvas.add(phase2_label)

# Checklist — three unchecked items that get checked one by one
checklist = Checklist(
    'Design mockups',
    'Write unit tests',
    'Deploy to staging',
    x=250, y=300, font_size=26, spacing=1.8,
    check_color=GREEN, uncheck_color='#444',
    creation=3.0,
)
checklist.fadein(3.1, 3.5)
checklist.check_item(0, start=3.8, end=4.2)
checklist.check_item(1, start=4.4, end=4.8)
checklist.check_item(2, start=5.0, end=5.4)
checklist.fadeout(5.5, 6.0)
canvas.add(checklist)

checklist_label = Text(
    text='Checklist', x=350, y=275, font_size=16,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
checklist_label.fadein(3.1, 3.5)
checklist_label.fadeout(5.5, 6.0)
canvas.add(checklist_label)

# Stepper — advances from step 1 to step 4
stepper = Stepper(
    ['Plan', 'Build', 'Test', 'Ship'],
    x=750, y=400, spacing=140, radius=22,
    active=0, direction='horizontal', font_size=14,
    active_color=CYAN, inactive_color='#444',
    creation=3.0,
)
stepper.fadein(3.2, 3.6)
stepper.advance(0, 1, start=3.9, end=4.3)
stepper.advance(1, 2, start=4.5, end=4.9)
stepper.advance(2, 3, start=5.1, end=5.5)
stepper.fadeout(5.5, 6.0)
canvas.add(stepper)

stepper_label = Text(
    text='Stepper', x=960, y=340, font_size=16,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
stepper_label.fadein(3.2, 3.6)
stepper_label.fadeout(5.5, 6.0)
canvas.add(stepper_label)

# =============================================================================
# Phase 3 (6-9s): SpeechBubble + Tooltip
# =============================================================================

phase3_label = Text(
    text='SpeechBubble & Tooltip', x=960, y=180, font_size=36,
    fill=WHITE, stroke_width=0, text_anchor='middle',
)
phase3_label.fadein(6.0, 6.4)
phase3_label.fadeout(8.5, 9.0)
canvas.add(phase3_label)

# SpeechBubble popping in
bubble = SpeechBubble(
    text='Hello, world!', x=250, y=350, font_size=24, padding=16,
    width=240, height=60, corner_radius=12,
    box_fill='#1e1e2e', box_opacity=0.95, text_color=WHITE,
    tail_direction='down', tail_width=24, tail_height=20,
    creation=6.0,
)
bubble.fadein(6.2, 6.8)
bubble.fadeout(8.5, 9.0)
canvas.add(bubble)

bubble_label = Text(
    text='SpeechBubble', x=370, y=330, font_size=16,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
bubble_label.fadein(6.2, 6.8)
bubble_label.fadeout(8.5, 9.0)
canvas.add(bubble_label)

# A shape target for the tooltip
target_circle = Circle(cx=850, cy=420, r=40, fill=CYAN, fill_opacity=0.3,
                       stroke=CYAN, stroke_width=2, creation=6.0)
target_circle.fadein(6.3, 6.7)
target_circle.fadeout(8.5, 9.0)
canvas.add(target_circle)

target_label = Text(
    text='Hover target', x=850, y=480, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
target_label.fadein(6.3, 6.7)
target_label.fadeout(8.5, 9.0)
canvas.add(target_label)

# Tooltip appearing near the shape
tooltip = Tooltip(
    'Click to edit', target=target_circle,
    start=7.0, duration=1.8, font_size=18, padding=8,
    creation=6.0, z=10,
)
canvas.add(tooltip)

# Second bubble for variety
bubble2 = SpeechBubble(
    text='Nice work!', x=250, y=500, font_size=20, padding=12,
    width=180, height=48, corner_radius=10,
    box_fill='#2a2a3a', box_opacity=0.9, text_color=GREEN,
    tail_direction='left', tail_width=18, tail_height=16,
    creation=6.0,
)
bubble2.fadein(7.0, 7.5)
bubble2.fadeout(8.5, 9.0)
canvas.add(bubble2)

# =============================================================================
# Phase 4 (9-12s): Countdown + Meter + StatusIndicator
# =============================================================================

phase4_label = Text(
    text='Countdown & Indicators', x=960, y=180, font_size=36,
    fill=WHITE, stroke_width=0, text_anchor='middle',
)
phase4_label.fadein(9.0, 9.4)
phase4_label.fadeout(11.5, 12.0)
canvas.add(phase4_label)

# Countdown from 5 to 1
countdown = Countdown(
    start_value=5, end_value=1,
    x=400, y=450, font_size=120,
    start=9.3, end=11.8,
    creation=9.0,
    fill=CYAN, stroke_width=0,
)
countdown.fadein(9.1, 9.5)
countdown.fadeout(11.5, 12.0)
canvas.add(countdown)

countdown_label = Text(
    text='Countdown', x=400, y=340, font_size=16,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
countdown_label.fadein(9.1, 9.5)
countdown_label.fadeout(11.5, 12.0)
canvas.add(countdown_label)

# Meter (vertical bar)
meter = Meter(
    value=0.75, x=750, y=350, width=35, height=160,
    direction='vertical', fill_color=GREEN, bg_color='#222',
    border_color='#666', creation=9.0,
)
meter.fadein(9.2, 9.6)
meter.fadeout(11.5, 12.0)
canvas.add(meter)

meter_label = Text(
    text='Meter (75%)', x=768, y=530, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
meter_label.fadein(9.2, 9.6)
meter_label.fadeout(11.5, 12.0)
canvas.add(meter_label)

# Second meter (horizontal)
meter2 = Meter(
    value=0.45, x=850, y=350, width=200, height=30,
    direction='horizontal', fill_color=ORANGE, bg_color='#222',
    border_color='#666', creation=9.0,
)
meter2.fadein(9.3, 9.7)
meter2.fadeout(11.5, 12.0)
canvas.add(meter2)

meter2_label = Text(
    text='Meter (45%)', x=950, y=395, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
meter2_label.fadein(9.3, 9.7)
meter2_label.fadeout(11.5, 12.0)
canvas.add(meter2_label)

# StatusIndicators
status1 = StatusIndicator('API Server', status='online', x=850, y=440, font_size=18,
                          creation=9.0)
status1.fadein(9.4, 9.8)
status1.fadeout(11.5, 12.0)
canvas.add(status1)

status2 = StatusIndicator('Database', status='warning', x=850, y=475, font_size=18,
                          creation=9.0)
status2.fadein(9.5, 9.9)
status2.fadeout(11.5, 12.0)
canvas.add(status2)

status3 = StatusIndicator('CDN Cache', status='offline', x=850, y=510, font_size=18,
                          creation=9.0)
status3.fadein(9.6, 10.0)
status3.fadeout(11.5, 12.0)
canvas.add(status3)

status_label = Text(
    text='StatusIndicator', x=920, y=420, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
status_label.fadein(9.4, 9.8)
status_label.fadeout(11.5, 12.0)
canvas.add(status_label)

# =============================================================================
# Render
# =============================================================================
if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
