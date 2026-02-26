import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/status_meter_breadcrumb')
canvas.set_background()

title = Text(text='StatusIndicator, Meter & Breadcrumb', x=960, y=40,
             font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# --- Status Indicators ---
si_label = Text(text='Service Status', x=50, y=110,
                font_size=20, fill='#aaa', stroke_width=0)
si_label.fadein(0.8, 1.5)

s1 = StatusIndicator('API Gateway', status='online', x=50, y=150)
s1.fadein(1, 2)

s2 = StatusIndicator('Database', status='online', x=50, y=185)
s2.fadein(1.2, 2.2)

s3 = StatusIndicator('Auth Service', status='warning', x=50, y=220)
s3.fadein(1.4, 2.4)

s4 = StatusIndicator('Email Service', status='offline', x=50, y=255)
s4.fadein(1.6, 2.6)

s5 = StatusIndicator('CDN', status='pending', x=50, y=290)
s5.fadein(1.8, 2.8)

# --- Meters ---
m_label = Text(text='System Meters', x=400, y=110,
               font_size=20, fill='#aaa', stroke_width=0)
m_label.fadein(0.8, 1.5)

m1 = Meter(value=0.85, x=400, y=140, fill_color='#83C167')
m1.fadein(1, 2)

m2 = Meter(value=0.6, x=450, y=140, fill_color='#58C4DD')
m2.fadein(1.2, 2.2)

m3 = Meter(value=0.35, x=500, y=140, fill_color='#FFFF00')
m3.fadein(1.4, 2.4)

m4 = Meter(value=0.92, x=550, y=140, fill_color='#FF6B6B')
m4.fadein(1.6, 2.6)

# Horizontal meter
m5 = Meter(value=0.7, x=400, y=320, width=200, height=25,
           direction='horizontal', fill_color='#58C4DD')
m5.fadein(1.8, 2.8)

# --- Breadcrumbs ---
bc_label = Text(text='Navigation Breadcrumbs', x=50, y=430,
                font_size=20, fill='#aaa', stroke_width=0)
bc_label.fadein(0.8, 1.5)

bc1 = Breadcrumb('Home', 'Products', 'Electronics', 'Laptops',
                 x=50, y=470, font_size=20)
bc1.fadein(1, 2)

bc2 = Breadcrumb('Dashboard', 'Settings', 'Security',
                 x=50, y=510, font_size=18, active_index=1,
                 active_color='#83C167')
bc2.fadein(1.3, 2.3)

canvas.add_objects(title, si_label, s1, s2, s3, s4, s5,
                   m_label, m1, m2, m3, m4, m5,
                   bc_label, bc1, bc2)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
