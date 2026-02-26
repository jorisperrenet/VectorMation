import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/checklist_stepper_tagcloud')
canvas.set_background()

title = Text(text='Checklist, Stepper & Tag Cloud', x=960, y=40,
             font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Checklist ---
cl = Checklist(
    ('Set up environment', True),
    ('Install dependencies', True),
    ('Write tests', False),
    ('Deploy to production', False),
    x=50, y=120, font_size=22,
)
cl.fadein(1, 2)

cl_label = Text(text='Project Checklist', x=50, y=95,
                font_size=18, fill='#aaa', stroke_width=0)
cl_label.fadein(0.8, 1.5)

# --- Stepper (horizontal) ---
st = Stepper(['Setup', 'Config', 'Build', 'Test', 'Deploy'],
             x=600, y=140, spacing=130, active=2,
             active_color='#58C4DD', inactive_color='#444')
st.fadein(1, 2)

st_label = Text(text='Pipeline Steps', x=600, y=95,
                font_size=18, fill='#aaa', stroke_width=0)
st_label.fadein(0.8, 1.5)

# --- Stepper (vertical) ---
st2 = Stepper(3, x=1400, y=120, spacing=80, active=1,
              direction='vertical', active_color='#83C167')
st2.fadein(1.5, 2.5)

st2_label = Text(text='Vertical Stepper', x=1400, y=95,
                 font_size=18, fill='#aaa', stroke_width=0)
st2_label.fadein(0.8, 1.5)

# --- Tag Cloud ---
tc = TagCloud([
    ('Python', 10), ('Machine Learning', 9), ('Data Science', 8),
    ('TensorFlow', 7), ('Neural Networks', 7), ('Deep Learning', 6),
    ('NLP', 5), ('Computer Vision', 5), ('Statistics', 4),
    ('PyTorch', 6), ('Pandas', 4), ('NumPy', 3),
    ('Scikit-learn', 5), ('API', 3), ('Cloud', 4),
], x=50, y=400, width=800, min_font=16, max_font=44)
tc.fadein(1.5, 2.5)

tc_label = Text(text='Tag Cloud', x=50, y=380,
                font_size=18, fill='#aaa', stroke_width=0)
tc_label.fadein(0.8, 1.5)

canvas.add_objects(title, cl, cl_label, st, st_label,
                   st2, st2_label, tc, tc_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
