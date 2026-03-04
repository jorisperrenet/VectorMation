from vectormation.objects import *

COLS = 5
ROW_H = 220
COL_W = 1920 // COLS
TITLE_Y = 50
FIRST_ROW = 120
N_ROWS = 5
COLORS = ['#58C4DD', '#83C167', '#FC6255', '#F0AC5F', '#9A72AC', '#5CD0B3']

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 60

title = Text(text='UI Widgets', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
objs = [title]

# ── Row 0 ────────────────────────────────────────────────────────────────

# (0,0) Badge
lbl = Text(text='Badge', x=col_x(0), y=lbl_y(0), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
b1 = Badge('v2.0', x=col_x(0) - 80, y=obj_y(0), bg_color='#3498DB')
b2 = Badge('NEW', x=col_x(0), y=obj_y(0), bg_color='#E74C3C')
b3 = Badge('OK', x=col_x(0) + 80, y=obj_y(0), bg_color='#2ECC71')
b4 = Badge('Beta', x=col_x(0) - 40, y=obj_y(0) + 40, bg_color='#9B59B6', text_color='#fff')
b5 = Badge('Pro', x=col_x(0) + 40, y=obj_y(0) + 40, bg_color='#F39C12')
objs.extend([lbl, b1, b2, b3, b4, b5])

# (1,0) Label
lbl = Text(text='Label', x=col_x(1), y=lbl_y(0), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
l1 = Label('Annotation', x=col_x(1), y=obj_y(0), font_size=20)
l2 = Label('Note', x=col_x(1), y=obj_y(0) + 50, font_size=16)
objs.extend([lbl, l1, l2])

# (2,0) TextBox
lbl = Text(text='TextBox', x=col_x(2), y=lbl_y(0), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
tb1 = TextBox('Enter name...', x=col_x(2) - 130, y=obj_y(0), width=260,
              font_size=16, box_fill='#1e1e2e')
tb2 = TextBox('Search', x=col_x(2) - 130, y=obj_y(0) + 50, width=260,
              font_size=16, box_fill='#222', text_color='#58C4DD')
objs.extend([lbl, tb1, tb2])

# (3,0) SpeechBubble
lbl = Text(text='SpeechBubble', x=col_x(3), y=lbl_y(0), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
sb1 = SpeechBubble('Hello!', x=col_x(3) - 100, y=obj_y(0), font_size=16,
                   width=160, height=45, box_fill='#2C3E50')
sb2 = SpeechBubble('Nice!', x=col_x(3) + 50, y=obj_y(0) + 40, font_size=14,
                   width=100, height=40, box_fill='#1a5276', tail_direction='left')
objs.extend([lbl, sb1, sb2])

# (4,0) StatusIndicator
lbl = Text(text='StatusIndicator', x=col_x(4), y=lbl_y(0), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
si1 = StatusIndicator('API Server', status='online', x=col_x(4) - 80, y=obj_y(0))
si2 = StatusIndicator('Database', status='warning', x=col_x(4) - 80, y=obj_y(0) + 30)
si3 = StatusIndicator('Cache', status='offline', x=col_x(4) - 80, y=obj_y(0) + 60)
si4 = StatusIndicator('Queue', status='pending', x=col_x(4) - 80, y=obj_y(0) + 90)
objs.extend([lbl, si1, si2, si3, si4])

# ── Row 1 ────────────────────────────────────────────────────────────────

# (0,1) Checklist
lbl = Text(text='Checklist', x=col_x(0), y=lbl_y(1), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
cl = Checklist(('Design', True), ('Implement', True), 'Test', 'Deploy',
               x=col_x(0) - 80, y=obj_y(1), font_size=16, spacing=1.3)
objs.extend([lbl, cl])

# (1,1) Stepper
lbl = Text(text='Stepper', x=col_x(1), y=lbl_y(1), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
st = Stepper(['Cart', 'Pay', 'Done'], x=col_x(1) - 130, y=obj_y(1) + 20,
             spacing=110, radius=14, active=1, font_size=12)
objs.extend([lbl, st])

# (2,1) Breadcrumb
lbl = Text(text='Breadcrumb', x=col_x(2), y=lbl_y(1), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
bc = Breadcrumb('Home', 'Products', 'Widgets',
                x=col_x(2) - 120, y=obj_y(1) + 10, font_size=16)
objs.extend([lbl, bc])

# (3,1) Countdown
lbl = Text(text='Countdown', x=col_x(3), y=lbl_y(1), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
cd = Countdown(start_value=5, end_value=0, x=col_x(3), y=obj_y(1) + 50,
               font_size=72, start=0, end=0.01)
objs.extend([lbl, cd])

# (4,1) CircularProgressBar
lbl = Text(text='CircularProgressBar', x=col_x(4), y=lbl_y(1), font_size=14,
           fill='#888', stroke_width=0, text_anchor='middle')
cpb = CircularProgressBar(72, x=col_x(4), y=obj_y(1) + 55, radius=45,
                          stroke_width=8, font_size=20)
objs.extend([lbl, cpb])

# ── Row 2 ────────────────────────────────────────────────────────────────

# (0,2) Meter
lbl = Text(text='Meter', x=col_x(0), y=lbl_y(2), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
m1 = Meter(value=0.8, x=col_x(0) - 60, y=obj_y(2), width=20, height=110,
           fill_color='#2ECC71')
m2 = Meter(value=0.5, x=col_x(0) - 20, y=obj_y(2), width=20, height=110,
           fill_color='#F39C12')
m3 = Meter(value=0.3, x=col_x(0) + 20, y=obj_y(2), width=20, height=110,
           fill_color='#E74C3C')
objs.extend([lbl, m1, m2, m3])

# (1,2) IconGrid
lbl = Text(text='IconGrid', x=col_x(1), y=lbl_y(2), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
ig = IconGrid([(6, '#3498DB'), (3, '#E74C3C'), (1, '#2ECC71')],
              x=col_x(1) - 60, y=obj_y(2), cols=5, size=16, gap=4)
objs.extend([lbl, ig])

# (2,2) DimensionLine
lbl = Text(text='DimensionLine', x=col_x(2), y=lbl_y(2), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
dim_rect = Rectangle(width=140, height=70, x=col_x(2) - 70, y=obj_y(2),
                     fill='#1e1e2e', fill_opacity=0.5, stroke='#555', stroke_width=1)
dl1 = DimensionLine((col_x(2) - 70, obj_y(2)), (col_x(2) + 70, obj_y(2)),
                    label='140px', offset=-18, font_size=12)
dl2 = DimensionLine((col_x(2) + 70, obj_y(2)), (col_x(2) + 70, obj_y(2) + 70),
                    label='70px', offset=18, font_size=12)
objs.extend([lbl, dim_rect, dl1, dl2])

# (3,2) Bracket
lbl = Text(text='Bracket', x=col_x(3), y=lbl_y(2), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
items = VCollection(
    Text(text='A', x=col_x(3) - 60, y=obj_y(2) + 10, font_size=20,
         fill='#58C4DD', stroke_width=0, text_anchor='middle'),
    Text(text='B', x=col_x(3), y=obj_y(2) + 10, font_size=20,
         fill='#58C4DD', stroke_width=0, text_anchor='middle'),
    Text(text='C', x=col_x(3) + 60, y=obj_y(2) + 10, font_size=20,
         fill='#58C4DD', stroke_width=0, text_anchor='middle'),
)
br = Bracket(x=col_x(3) - 80, y=obj_y(2) + 30, width=160, height=14,
             direction='down', text='group', font_size=13, stroke='#888')
objs.extend([lbl, items, br])

# (4,2) LabeledArrow
lbl = Text(text='LabeledArrow', x=col_x(4), y=lbl_y(2), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
la = LabeledArrow(x1=col_x(4) - 120, y1=obj_y(2) + 30,
                  x2=col_x(4) + 120, y2=obj_y(2) + 30,
                  label='flow', font_size=14, stroke='#58C4DD')
objs.extend([lbl, la])

# ── Row 3 ────────────────────────────────────────────────────────────────

# (0,3) LabeledLine
lbl = Text(text='LabeledLine', x=col_x(0), y=lbl_y(3), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
ll = LabeledLine(x1=col_x(0) - 120, y1=obj_y(3) + 30,
                 x2=col_x(0) + 120, y2=obj_y(3) + 30,
                 label='link', font_size=14, stroke='#888', stroke_width=1)
objs.extend([lbl, ll])

# (1,3) Underline
lbl = Text(text='Underline', x=col_x(1), y=lbl_y(3), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
ul_text = Text(text='Emphasis', x=col_x(1), y=obj_y(3) + 20, font_size=26,
               fill='#fff', stroke_width=0, text_anchor='middle')
ul = Underline(ul_text, buff=6, stroke='#58C4DD', stroke_width=2)
objs.extend([lbl, ul_text, ul])

# (2,3) Filmstrip
lbl = Text(text='Filmstrip', x=col_x(2), y=lbl_y(3), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
fs = Filmstrip(['Intro', 'Build', 'Result'], x=col_x(2) - 150, y=obj_y(3),
               frame_width=90, frame_height=60, spacing=8, font_size=11)
objs.extend([lbl, fs])

# (3,3) Divider
lbl = Text(text='Divider', x=col_x(3), y=lbl_y(3), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
div1 = Divider(x=col_x(3) - 130, y=obj_y(3) + 10, length=260, label='Section')
div2 = Divider(x=col_x(3) - 130, y=obj_y(3) + 60, length=260, stroke='#444')
objs.extend([lbl, div1, div2])

# (4,3) TagCloud
lbl = Text(text='TagCloud', x=col_x(4), y=lbl_y(3), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
tc = TagCloud([('Python', 10), ('SVG', 8), ('Anim', 7), ('UI', 5),
               ('Design', 6), ('Vector', 4), ('Code', 3)],
              x=col_x(4) - 130, y=obj_y(3), width=260, min_font=12, max_font=28)
objs.extend([lbl, tc])

# ── Row 4 ────────────────────────────────────────────────────────────────

# (0,4) NumberedList
lbl = Text(text='NumberedList', x=col_x(0), y=lbl_y(4), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
nl = NumberedList('Set up env', 'Install deps', 'Run tests', 'Deploy',
                  x=col_x(0) - 90, y=obj_y(4), font_size=16)
objs.extend([lbl, nl])

# (1,4) BulletedList
lbl = Text(text='BulletedList', x=col_x(1), y=lbl_y(4), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
bl = BulletedList('Feature A', 'Feature B', 'Feature C',
                  x=col_x(1) - 90, y=obj_y(4), font_size=16, bullet='\u2022')
objs.extend([lbl, bl])

# (2,4) Paragraph
lbl = Text(text='Paragraph', x=col_x(2), y=lbl_y(4), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
pg = Paragraph('The quick brown fox', 'jumps over the lazy', 'dog.',
               x=col_x(2) - 100, y=obj_y(4), font_size=16, alignment='left')
objs.extend([lbl, pg])

# (3,4) Tooltip
lbl = Text(text='Tooltip', x=col_x(3), y=lbl_y(4), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
tt_target = Dot(cx=col_x(3), cy=obj_y(4) + 50, r=10,
                fill='#F0AC5F', stroke_width=0)
tt = Tooltip('Hover info', tt_target, start=0, duration=999, font_size=14)
objs.extend([lbl, tt_target, tt])

# (4,4) Callout
lbl = Text(text='Callout', x=col_x(4), y=lbl_y(4), font_size=16,
           fill='#888', stroke_width=0, text_anchor='middle')
target_circ = Circle(r=20, cx=col_x(4), cy=obj_y(4) + 10,
                     fill='#58C4DD', fill_opacity=0.7, stroke='#58C4DD')
co = Callout('Info', target_circ, direction='up', distance=50, font_size=14)
objs.extend([lbl, target_circ, co])

canvas.add_objects(*objs)

canvas.show()
