"""UI Widgets Demo — Badge, Callout, Divider, Breadcrumb, TagCloud, IconGrid, Filmstrip."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/ui_widgets')
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
PURPLE = '#9B59B6'
DARK_BG = '#1e1e2e'

# =============================================================================
# Phase 1 (0-4s): Callout, Dividers, Brackets
# =============================================================================

phase1_title = Text(
    text='Callout / Divider / Bracket', x=960, y=80, font_size=36,
    fill=WHITE, stroke_width=0, text_anchor='middle',
)
phase1_title.fadein(0.0, 0.4)
phase1_title.fadeout(3.5, 4.0)
canvas.add(phase1_title)

# --- Callout pointing at a target circle ---
target_dot = Dot(cx=350, cy=350, r=18, fill=CYAN, stroke_width=0)
target_dot.fadein(0.3, 0.6)
target_dot.fadeout(3.5, 4.0)
canvas.add(target_dot)

callout = Callout(
    'Target node', target=target_dot, direction='up', distance=70,
    font_size=20, padding=8, corner_radius=5, creation=0,
)
callout.fadein(0.5, 0.9)
callout.fadeout(3.5, 4.0)
canvas.add(callout)

callout_label = Text(
    text='Callout', x=350, y=200, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
callout_label.fadein(0.5, 0.9)
callout_label.fadeout(3.5, 4.0)
canvas.add(callout_label)

# Second callout from the right side
target_dot2 = Dot(cx=350, cy=500, r=14, fill=ORANGE, stroke_width=0)
target_dot2.fadein(0.6, 0.9)
target_dot2.fadeout(3.5, 4.0)
canvas.add(target_dot2)

callout2 = Callout(
    'Alert!', target=target_dot2, direction='right', distance=80,
    font_size=18, padding=6, corner_radius=4, creation=0,
)
callout2.fadein(0.8, 1.2)
callout2.fadeout(3.5, 4.0)
canvas.add(callout2)

# --- Dividers ---
# Horizontal divider with label
divider1 = Divider(
    x=650, y=300, length=600, direction='horizontal',
    label='SECTION', font_size=14, gap=10,
    stroke='#555', stroke_width=1,
)
divider1.fadein(0.4, 0.8)
divider1.fadeout(3.5, 4.0)
canvas.add(divider1)

div_label = Text(
    text='Divider (labeled)', x=950, y=278, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
div_label.fadein(0.4, 0.8)
div_label.fadeout(3.5, 4.0)
canvas.add(div_label)

# Plain horizontal divider
divider2 = Divider(
    x=650, y=380, length=600, direction='horizontal',
    stroke='#444', stroke_width=2,
)
divider2.fadein(0.6, 1.0)
divider2.fadeout(3.5, 4.0)
canvas.add(divider2)

div_label2 = Text(
    text='Divider (plain)', x=950, y=358, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
div_label2.fadein(0.6, 1.0)
div_label2.fadeout(3.5, 4.0)
canvas.add(div_label2)

# Vertical divider
divider3 = Divider(
    x=1350, y=400, length=250, direction='vertical',
    stroke='#666', stroke_width=1,
)
divider3.fadein(0.8, 1.2)
divider3.fadeout(3.5, 4.0)
canvas.add(divider3)

div_label3 = Text(
    text='Vertical', x=1380, y=410, font_size=13,
    fill=GREY, stroke_width=0,
)
div_label3.fadein(0.8, 1.2)
div_label3.fadeout(3.5, 4.0)
canvas.add(div_label3)

# --- Brackets ---
bracket1 = Bracket(
    x=650, y=440, width=250, height=18,
    direction='down', stroke=CYAN, stroke_width=2,
    text='span A', font_size=14, text_color=CYAN,
)
bracket1.fadein(1.0, 1.4)
bracket1.fadeout(3.5, 4.0)
canvas.add(bracket1)

bracket2 = Bracket(
    x=940, y=440, width=180, height=18,
    direction='down', stroke=GREEN, stroke_width=2,
    text='span B', font_size=14, text_color=GREEN,
)
bracket2.fadein(1.2, 1.6)
bracket2.fadeout(3.5, 4.0)
canvas.add(bracket2)

bracket_label = Text(
    text='Bracket', x=860, y=418, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
bracket_label.fadein(1.0, 1.4)
bracket_label.fadeout(3.5, 4.0)
canvas.add(bracket_label)

# --- DimensionLine ---
dim_line = DimensionLine(
    p1=(650, 580), p2=(1100, 580), offset=25,
    font_size=16, tick_size=10,
    stroke='#aaa', stroke_width=1,
)
dim_line.fadein(1.4, 1.8)
dim_line.fadeout(3.5, 4.0)
canvas.add(dim_line)

dim_label = Text(
    text='DimensionLine', x=875, y=630, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
dim_label.fadein(1.4, 1.8)
dim_label.fadeout(3.5, 4.0)
canvas.add(dim_label)

# =============================================================================
# Phase 2 (4-8s): Breadcrumb, TagCloud, IconGrid
# =============================================================================

phase2_title = Text(
    text='Breadcrumb / TagCloud / IconGrid', x=960, y=80, font_size=36,
    fill=WHITE, stroke_width=0, text_anchor='middle',
)
phase2_title.fadein(4.0, 4.4)
phase2_title.fadeout(7.5, 8.0)
canvas.add(phase2_title)

# --- Breadcrumb trail ---
breadcrumb = Breadcrumb(
    'Home', 'Products', 'Electronics', 'Headphones',
    x=150, y=180, font_size=22, gap=10,
    active_color=CYAN, inactive_color='#777',
)
breadcrumb.fadein(4.2, 4.6)
breadcrumb.fadeout(7.5, 8.0)
canvas.add(breadcrumb)

bc_label = Text(
    text='Breadcrumb', x=150, y=155, font_size=14,
    fill=GREY, stroke_width=0,
)
bc_label.fadein(4.2, 4.6)
bc_label.fadeout(7.5, 8.0)
canvas.add(bc_label)

# Second breadcrumb with different separator
breadcrumb2 = Breadcrumb(
    'Dashboard', 'Settings', 'Profile',
    x=150, y=240, font_size=20, separator='/', gap=8,
    active_color=GREEN, inactive_color='#666',
)
breadcrumb2.fadein(4.5, 4.9)
breadcrumb2.fadeout(7.5, 8.0)
canvas.add(breadcrumb2)

# --- TagCloud ---
tag_data = [
    ('Python', 10), ('JavaScript', 8), ('Rust', 7),
    ('TypeScript', 6), ('Go', 5), ('C++', 4),
    ('Java', 6), ('Kotlin', 3), ('Swift', 4),
    ('Ruby', 3), ('Haskell', 2), ('Elixir', 2),
    ('Scala', 3), ('Dart', 2), ('Zig', 4),
]
tag_cloud = TagCloud(
    tag_data, x=150, y=320, width=700,
    min_font=16, max_font=44,
    colors=[CYAN, GREEN, ORANGE, PINK, YELLOW, PURPLE, '#4FC3F7', '#AED581'],
)
tag_cloud.fadein(4.6, 5.2)
tag_cloud.fadeout(7.5, 8.0)
canvas.add(tag_cloud)

tc_label = Text(
    text='TagCloud', x=150, y=300, font_size=14,
    fill=GREY, stroke_width=0,
)
tc_label.fadein(4.6, 5.2)
tc_label.fadeout(7.5, 8.0)
canvas.add(tc_label)

# --- IconGrid (circle-based) ---
icon_data_circles = [
    (15, GREEN),
    (10, ORANGE),
    (5, PINK),
    (10, GREY),
]
icon_grid1 = IconGrid(
    icon_data_circles, x=1000, y=180, cols=8, size=20, gap=5,
    shape='circle',
)
icon_grid1.fadein(5.0, 5.5)
icon_grid1.fadeout(7.5, 8.0)
canvas.add(icon_grid1)

ig_label1 = Text(
    text='IconGrid (circles)', x=1100, y=160, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
ig_label1.fadein(5.0, 5.5)
ig_label1.fadeout(7.5, 8.0)
canvas.add(ig_label1)

# IconGrid (square-based)
icon_data_squares = [
    (12, CYAN),
    (8, PURPLE),
    (6, YELLOW),
    (14, '#444'),
]
icon_grid2 = IconGrid(
    icon_data_squares, x=1000, y=380, cols=8, size=18, gap=4,
    shape='square',
)
icon_grid2.fadein(5.4, 5.9)
icon_grid2.fadeout(7.5, 8.0)
canvas.add(icon_grid2)

ig_label2 = Text(
    text='IconGrid (squares)', x=1100, y=360, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
ig_label2.fadein(5.4, 5.9)
ig_label2.fadeout(7.5, 8.0)
canvas.add(ig_label2)

# --- Label ---
label1 = Label('Important', x=1100, y=570, font_size=22, padding=10, corner_radius=5)
label1.fadein(5.8, 6.2)
label1.fadeout(7.5, 8.0)
canvas.add(label1)

label2 = Label('Note', x=1300, y=570, font_size=18, padding=8, corner_radius=4)
label2.fadein(6.0, 6.4)
label2.fadeout(7.5, 8.0)
canvas.add(label2)

lbl_label = Text(
    text='Label', x=1200, y=545, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
lbl_label.fadein(5.8, 6.2)
lbl_label.fadeout(7.5, 8.0)
canvas.add(lbl_label)

# =============================================================================
# Phase 3 (8-12s): Filmstrip, Lists, Variable
# =============================================================================

phase3_title = Text(
    text='Filmstrip / Lists / Variable', x=960, y=80, font_size=36,
    fill=WHITE, stroke_width=0, text_anchor='middle',
)
phase3_title.fadein(8.0, 8.4)
phase3_title.fadeout(11.5, 12.0)
canvas.add(phase3_title)

# --- Filmstrip ---
filmstrip = Filmstrip(
    ['Intro', 'Setup', 'Demo', 'Outro'],
    x=120, y=140, frame_width=170, frame_height=110,
    spacing=16, font_size=14,
)
filmstrip.fadein(8.2, 8.7)
# Sequentially highlight each frame
filmstrip.highlight_frame(0, start=8.8, end=9.4, color=CYAN)
filmstrip.highlight_frame(1, start=9.2, end=9.8, color=GREEN)
filmstrip.highlight_frame(2, start=9.6, end=10.2, color=ORANGE)
filmstrip.highlight_frame(3, start=10.0, end=10.6, color=PINK)
filmstrip.fadeout(11.5, 12.0)
canvas.add(filmstrip)

fs_label = Text(
    text='Filmstrip', x=480, y=125, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
fs_label.fadein(8.2, 8.7)
fs_label.fadeout(11.5, 12.0)
canvas.add(fs_label)

# --- BulletedList ---
bullet_list = BulletedList(
    'Design the interface',
    'Implement core logic',
    'Write test suite',
    'Deploy to production',
    x=120, y=340, font_size=24, line_spacing=1.6,
    fill=WHITE, stroke_width=0,
)
bullet_list.fadein(8.5, 9.0)
bullet_list.fadeout(11.5, 12.0)
canvas.add(bullet_list)

bl_label = Text(
    text='BulletedList', x=120, y=315, font_size=14,
    fill=GREY, stroke_width=0,
)
bl_label.fadein(8.5, 9.0)
bl_label.fadeout(11.5, 12.0)
canvas.add(bl_label)

# --- NumberedList ---
numbered_list = NumberedList(
    'Initialize project',
    'Configure database',
    'Build API endpoints',
    'Add authentication',
    x=620, y=340, font_size=24, line_spacing=1.6,
    fill=WHITE, stroke_width=0,
)
numbered_list.fadein(8.8, 9.3)
numbered_list.fadeout(11.5, 12.0)
canvas.add(numbered_list)

nl_label = Text(
    text='NumberedList', x=620, y=315, font_size=14,
    fill=GREY, stroke_width=0,
)
nl_label.fadein(8.8, 9.3)
nl_label.fadeout(11.5, 12.0)
canvas.add(nl_label)

# --- Variable with animated value ---
var = Variable(
    label='progress', value=0, fmt='{:.1f}%',
    x=1250, y=370, font_size=36,
)
var.fadein(9.0, 9.4)
var.animate_value(100, start=9.5, end=11.2)
var.fadeout(11.5, 12.0)
canvas.add(var)

var_label = Text(
    text='Variable (animated)', x=1250, y=330, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
var_label.fadein(9.0, 9.4)
var_label.fadeout(11.5, 12.0)
canvas.add(var_label)

# --- StatusIndicators (different states) ---
status_online = StatusIndicator(
    'Build passing', status='online', x=1100, y=480, font_size=18,
)
status_online.fadein(9.2, 9.6)
status_online.fadeout(11.5, 12.0)
canvas.add(status_online)

status_warn = StatusIndicator(
    'Memory usage high', status='warning', x=1100, y=515, font_size=18,
)
status_warn.fadein(9.4, 9.8)
status_warn.fadeout(11.5, 12.0)
canvas.add(status_warn)

status_off = StatusIndicator(
    'Backup server down', status='offline', x=1100, y=550, font_size=18,
)
status_off.fadein(9.6, 10.0)
status_off.fadeout(11.5, 12.0)
canvas.add(status_off)

status_pending = StatusIndicator(
    'Deploy queued', status='pending', x=1100, y=585, font_size=18,
)
status_pending.fadein(9.8, 10.2)
status_pending.fadeout(11.5, 12.0)
canvas.add(status_pending)

si_label = Text(
    text='StatusIndicator', x=1200, y=455, font_size=14,
    fill=GREY, stroke_width=0, text_anchor='middle',
)
si_label.fadein(9.2, 9.6)
si_label.fadeout(11.5, 12.0)
canvas.add(si_label)

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
