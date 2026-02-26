import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/progress_scoreboard')
canvas.set_background()

title = Text(text='Circular Progress, Population Pyramid, Data Table & Scoreboard',
             x=960, y=40, font_size=28, fill='#58C4DD', stroke_width=0,
             text_anchor='middle')
title.write(0, 1)

# --- Circular Progress Bars ---
cp1 = CircularProgressBar(85, x=150, y=200, radius=70, bar_color='#83C167')
cp1.fadein(1, 1.5)
cp1_lbl = Text(text='CPU', x=150, y=290, font_size=16, fill='#aaa',
               stroke_width=0, text_anchor='middle')
cp1_lbl.fadein(1, 1.5)

cp2 = CircularProgressBar(62, x=350, y=200, radius=70, bar_color='#58C4DD')
cp2.fadein(1.2, 1.7)
cp2_lbl = Text(text='Memory', x=350, y=290, font_size=16, fill='#aaa',
               stroke_width=0, text_anchor='middle')
cp2_lbl.fadein(1.2, 1.7)

cp3 = CircularProgressBar(23, x=550, y=200, radius=70, bar_color='#FF6B6B')
cp3.fadein(1.4, 1.9)
cp3_lbl = Text(text='Disk', x=550, y=290, font_size=16, fill='#aaa',
               stroke_width=0, text_anchor='middle')
cp3_lbl.fadein(1.4, 1.9)

# --- Population Pyramid ---
ax = Axes(x_range=(-50, 50), y_range=(0, 6),
          plot_width=350, plot_height=250, x=750, y=100)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

pp = ax.plot_population_pyramid(
    [1, 2, 3, 4, 5],
    [40, 35, 25, 15, 8],   # left (male)
    [38, 33, 27, 18, 10],  # right (female)
    left_color='#58C4DD', right_color='#FF79C6')
pp.fadein(2, 3)

pyramid_label = Text(text='Population Pyramid', x=925, y=90,
                     font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
pyramid_label.fadein(1, 1.5)

# --- Data Table ---
ax2 = Axes(x_range=(0, 5), y_range=(0, 10),
           plot_width=300, plot_height=180, x=50, y=400)
ax2.add_coordinates()
ax2.fadein(0.5, 1.5)

bars = ax2.plot_bar([1, 2, 3, 4], [6, 9, 4, 8], width=0.6)
bars.fadein(2, 2.5)

dt = ax2.add_data_table(['Q1', 'Q2', 'Q3', 'Q4'], [['6', '9', '4', '8']])
dt.fadein(2, 2.5)

table_label = Text(text='Chart + Data Table', x=200, y=390,
                   font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
table_label.fadein(1, 1.5)

# --- Scoreboard ---
entries = [('Points', '2,847'), ('Level', '42'), ('Streak', '15'),
           ('Rank', '#3')]
sb = Scoreboard(entries, x=550, y=450, col_width=180, row_height=55, font_size=30)
sb.fadein(2.5, 3.5)

sb_label = Text(text='Scoreboard', x=910, y=430,
                font_size=18, fill='#aaa', stroke_width=0, text_anchor='middle')
sb_label.fadein(1, 1.5)

canvas.add_objects(title, cp1, cp2, cp3, cp1_lbl, cp2_lbl, cp3_lbl,
                   ax, pp, pyramid_label, ax2, bars, dt, table_label,
                   sb, sb_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
