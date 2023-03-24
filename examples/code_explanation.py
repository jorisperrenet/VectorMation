from vectormation.objects import *


# Initialize the animation frame
canvas = VectorMathAnim(save_dir='svgs/code_explanation')
canvas.set_background()

### Draw the objects
## Making the upper SVG Video part
video_frame = Rectangle(300, 200, stroke_width=2, fill='grey', stroke='white', fill_opacity=1)
video_frame.center_to_pos()
play_button_circle = Circle(r=30, fill_opacity=0, stroke='black', stroke_width=4)
play_button_triangle = EquilateralTriangle(30, angle=90, fill='black', stroke_width=0, fill_opacity=1)
video_text = TexObject('SVG Video', fill='white', scale_x=5, scale_y=5)
video_text_height = video_text.bbox(0)[-1]
video_text.center_to_pos(posy=400-video_text_height/2-10)
video = VCollection(video_frame, play_button_circle, play_button_triangle, video_text)
video.shift(dy=-300)

## Making the Individual Frames part
# the frames
rects = []
for i in range(75, 776, 100):
    frame = Rectangle(150, 100, x=i, y=350+i/10, fill_opacity=1)
    rects.append(frame)
    frame_line = Line(x1=500, y1=300, x2=i+75, y2=350+i/10, stroke_width=2)
    rects.append(frame_line)
    frame_text = TexObject(f't={i/100}', fill='white', scale_x=2, scale_y=2)
    frame_text_height = frame_text.bbox(0)[-1]
    frame_text.center_to_pos(posx=i+75, posy=350+i/10+100+frame_text_height/2+5)
    rects.append(frame_text)
    frame_object = Circle(r=10, cx=i+75, cy=370+i/10, fill='blue', fill_opacity=1, stroke_width=0)
    frame_object.shift(dy=(i/100)**2)
    rects.append(frame_object)
# the text under the frames
frames_text = TexObject('Individual Frames', fill='white', scale_x=5, scale_y=5)
frames_text.center_to_pos(posy=555)
frames_subtext = TexObject('(collection of all objects at time $t$)', fill='white', scale_x=2.5, scale_y=2.5)
frames_subtext.center_to_pos(posy=595)
frames = VCollection(*rects + [frames_text, frames_subtext])

## Making an bottom object+attributes part
circle = Circle(r=70, cx=200, cy=750, fill='blue', fill_opacity=1, stroke_width=0)
object_text = TexObject('Object($t$)', fill='white', scale_x=4, scale_y=4)
object_text.center_to_pos(200, 850)
attr = TexObject('Attributes($t$)', fill='white', scale_x=4, scale_y=4)
attr.center_to_pos(500, 750)
line_to_attr = Line(x1=270+10, y1=750, x2=attr.bbox(0)[0]-10, y2=750, stroke_width=2)
attr_objects = []
attr_names = ['Show($t$)', 'Center($t$)', 'Radius($t$)', 'Styling($t$)']
for idx, a in enumerate(attr_names):
    text = TexObject(a, fill='white', scale_x=3, scale_y=3)
    text.center_to_pos(posx=800, posy=750+(idx-1.5)*70)
    attr_objects.append(text)
    line_to_text = Line(x1=attr.bbox(0)[0]+attr.bbox(0)[2]+10, y1=750, x2=text.bbox(0)[0]-10, y2=750+(idx-1.5)*70, stroke_linecap='round', stroke_width=2)
    attr_objects.append(line_to_text)
explanation = TexObject(r'\begin{center}Each object is comprised of attributes.\\Each attribute is a function of time.\end{center}', scale_x=2.5, scale_y=2.5)
explanation.center_to_pos(posx=500, posy=930)
object = VCollection(circle, object_text, line_to_attr, attr, *attr_objects, explanation)

# Add the objects to the canvas
canvas.add_objects(video, frames, object)

# Display the window
canvas.standard_display(fps=60)
