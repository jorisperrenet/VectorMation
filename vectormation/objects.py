"""Here we define all objects like squares, texobjects, morphobjects, ...
First we create a general object that defines the necessary functions and a fadein-fadeout function
"""
import sys
from abc import ABC, abstractmethod
from copy import copy, deepcopy
from bs4 import BeautifulSoup
from time import sleep
from svgpathtools import parse_path  # Write code yourself??? only bbox needed, NOTE: TODO
import math
import datetime

# Local imports
import vectormation.easings as easings
import vectormation.attributes as attributes
from vectormation.tex_file_writing import tex_content_to_svg_file
from vectormation.tex_file_writing import get_characters
from vectormation.utils import keyevent_to_string
from vectormation.window import SVGViewer  # NOTE: TODO is this import necessary or can we disable it
import vectormation.style as style
import vectormation.morphing as morphing

# MARKER: Above code is not checked, restucture files; NOTE: TODO

class VectorMathAnim:
    """Video where we can ask a frame at a certain time"""
    def __init__(self, save_dir, width=1000, height=1000):
        self.save_dir = save_dir  # Directory to save frames in
        self.filename = f'{save_dir}/gen.svg'
        self.width = width
        self.height = height
        self.viewbox = (0, 0, width, height)
        self.objects = {}  # {id(object): object}
        self.time = 0  # Time of the current video
        self.dt = 0
        self.start_anim = None
        self.end_anim = None
        self.animate = None
        self.background = None
        self.svgviewer = None

        # We need to set the save directory globally
        global save_directory
        save_directory = save_dir

    def set_background(self, creation=0, z=-1, **styling):
        """Sets the background of the animation (otherwise no background is added)"""
        if self.background != None:
            # The background already existed, discarding...
            del self.objects[id(self.background)]
        # Process the styling keyword arguments with a default black background
        st = style.Styling(styling, creation=creation, stroke_width=0)
        self.background = Rectangle(self.width, self.height, x=0, y=0, rx=0, ry=0, creation=creation, z=z, **st.kwargs())
        self.add_objects(self.background)

    def add_objects(self, *args):
        """Adding to a collection of all objects that must be displayed at some time"""
        for obj in args:
            obj_id = id(obj)
            self.objects[obj_id] = obj

    def write_frame(self, time=None, filename=None):
        """This combines all the svgs of objects alive at the canvas time"""
        if time == None:
            time = self.time  # The canvas time
        if filename == None:
            filename = self.filename

        # Write the svg data to the file
        with open(filename, 'w') as s:
            s.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            header = f"<svg version='1.1' xmlns='http://www.w3.org/2000/svg' " \
                     f"xmlns:xlink='http://www.w3.org/1999/xlink' " \
                     f"width='{self.width}' height='{self.height}' " \
                     f"viewBox='{' '.join(str(i) for i in self.viewbox)}'>\n"
            s.write(header)
            # Sorting based on the z property/draw order
            lst = []
            for obj in self.objects.values():
                if obj.show.at_time(time):
                    if not hasattr(obj, 'z'):
                        lst.append((0, obj))
                    else:
                        lst.append((obj.z.at_time(time), obj))

            # Add the objects
            for _, obj in sorted(lst, key=lambda x: x[0]):
                s.write(obj.to_svg(time) + '\n')

            # Close the header
            s.write("</svg>")

    def event(self, event):
        """Code to process any events from the animation window"""
        if event.__class__.__name__ == 'QMouseEvent':
            ### Display the mouse position in the top labels
            w, h = self.svgviewer.window.width(), self.svgviewer.window.height()
            svg_part = self.svgviewer.window.view.svgItem
            bounding = svg_part.boundingRect()
            bw, bh = bounding.width(), bounding.height()
            scale = svg_part.scale()
            w, h = bw*scale, bh*scale
            x, y = svg_part.pos().x(), svg_part.pos().y()
            # The x, y, w, h is the rectangle around the svgview part
            map_x, map_y = event.x(), event.y()
            # The relative position of the mouse
            rel_x, rel_y = (map_x-x)/w, (map_y-y)/h
            # The coordinates of the mouse with respect to the viewer
            view_x = rel_x * self.viewbox[2] + self.viewbox[0]
            view_y = rel_y * self.viewbox[3] + self.viewbox[1]

            # Add this information to the viewer
            self.svgviewer.window.xpos.setText(f'x={view_x:#.2f}')
            self.svgviewer.window.ypos.setText(f'y={view_y:#.2f}')
            # NOTE: TODO: Dragging does what?
        elif event.__class__.__name__ == 'QWheelEvent':
            ### Scrolling motion
            zoom = pow(1.2, event.pixelDelta().y() / 240.0)
            pos = event.x(), event.y()
            v = self.viewbox
            # Mouse position relative to the screen
            svg_part = self.svgviewer.window.view.svgItem
            rect = svg_part.boundingRect()
            rel_x = (pos[0]-svg_part.pos().x())/rect.width()
            rel_y = (pos[1]-svg_part.pos().y())/rect.height()
            rel_x, rel_y = max(min(rel_x, 1), 0), max(min(rel_y, 1), 0)
            # Change the viewbox
            new_width, new_height = v[2]/zoom, v[3]/zoom
            dw, dh = v[2]-new_width, v[3]-new_height
            self.viewbox = (v[0]+rel_x*dw, v[1]+rel_y*dh, new_width, new_height)
            self.redraw()
        elif event.__class__.__name__ == 'QKeyEvent':
            ### Actions for keypresses
            char = keyevent_to_string(event)
            if char == 'Q':
                print('Quitting...')
                sys.exit()
            elif char == 'R':
                # Restarting the animation
                self.time = self.start_anim
                self.frame_count = 0
            elif char == 'F':
                # Resetting window zoom
                self.viewbox = (0, 0, self.width, self.height)
                self.redraw()
            elif char == 'P':
                # Pausing (or toggling pause) of window
                self.animate = 1 - self.animate
                self.redraw()
        else:
            # Discard other events like window open events
            pass

    def redraw(self):
        """Force the svg viewer to redraw"""
        if self.svgviewer is None:
            raise BaseException('Cannot redraw, no svg viewer')
        self.write_frame()
        self.svgviewer.view(self.filename)

    def standard_display(self, start_time=0, end_time=None, fps=60):
        """Views the svg using the svg viewer
        renders with accuracy of about a millisecond on time
        If start_time < 0, we go that many seconds before the end"""
        self.svgviewer = SVGViewer(self)
        if end_time == None:
            # Animate to the last available frame, first we must find it
            end_time = max(obj.last_change for obj in self.objects.values())
            print(f'Found that the ending time is {end_time}.')
        self.end_anim = end_time
        # Set the starting time of the animation
        if start_time < 0:
            self.start_anim = end_time - start_time
        else:
            self.start_anim = start_time
        self.animate = True

        # Start animating at the start time and increase with dt
        # untill the end_time is reached
        self.time = start_time
        self.frame_count = 0
        self.dt = 1/fps
        while True:
            # Continue displaying and redrawing forever
            wait_till = datetime.datetime.now() + datetime.timedelta(seconds=self.dt)
            self.write_frame()
            self.svgviewer.view(self.filename, wait_till)

            if self.frame_count <= self.end_anim * fps:
                # Change progressbar
                prog = self.svgviewer.window.progress
                if end_time == 0:
                    prog.setValue(100)
                else:
                    prog.setValue(int(self.frame_count / (end_time*fps)*100))
                prog.setFormat(f'{self.frame_count}/{round(end_time*fps)}')

            # Increase the time so that we can draw the next frame
            if self.animate:
                self.time += self.dt
                self.time = min(self.time, end_time)  # to avoid rounding error affecting the display
                self.frame_count += 1


class VObject(ABC):  # Vector Object
    """This is the motherclass for all vector objects
    Having creation and destroying function implemented.
    Since an image is not a vector object this will not be a child
    (thus the fadein function and fadeout function will not be the
     same as for vector objects)
    """
    @abstractmethod
    def __init__(self, creation=0, z=0):
        # If we need to show the object
        self.show = attributes.Real(creation, True)
        # Specify the draw order
        self.z = attributes.Real(creation, z)

    @abstractmethod
    def to_svg(self, time):
        """Get the svg-specifyer of the object at this time"""
        pass

    @abstractmethod
    def last_change(self):
        """Get the time of the last change of this shape, the max of all attributes"""
        pass

    @abstractmethod
    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        """Shift the object dx and dy (without changing the transformation styling preferrably)
        If end_time is not None we animate the movement from start_time to end_time"""
        pass

    @abstractmethod
    def path(self, time):
        """Get the SVG-path-specifyer of the object (unadjusted for its transforms)"""
        pass

    def bbox(self, time):
        """Get the bounding rectangle in (xmin, ymin, width, height) at a certain time"""
        # Get the path specifyer of the object
        path = self.path(time)
        if not hasattr(self, 'styling'):
            # We do not need to adjust for the transform part of styling
            xmin, xmax, ymin, ymax = morphing.Path(path).bbox()
        else:
            transforms = self.styling.transform_style(time)
            if transforms == '':
                # No transforms to be done
                xmin, xmax, ymin, ymax = morphing.Path(path).bbox()
                return (xmin, ymin, xmax-xmin, ymax-ymin)
            transforms = transforms[1:].split(' ')
            xmin, xmax, ymin, ymax = morphing.Path(path).adjusted_bbox(*transforms)
        return (xmin, ymin, xmax-xmin, ymax-ymin)

    def center_to_pos(self, posx=500, posy=500, start_time=0, end_time=None, easing=easings.smooth):
        """Shifts the center to pos, and animates this from start_time to end_time
        Shifting is done with respect to the position at start_time."""
        xmin, ymin, width, height = self.bbox(start_time)
        dx, dy = posx-(xmin+width/2), posy-(ymin+height/2)
        self.shift(dx=dx, dy=dy, start_time=start_time, end_time=end_time, easing=easing)

    def brect(self, time=0, rx=0, ry=0, dpos=5, follow=True):
        """Returns the bounding rectangle (or surrounding rectangle) adjusted with dpos outward
        If time is specified creates the rectangle from time onward
        If follow = True, the rectangle will follow the object."""
        if not follow:  # Get the bounding rectangle once
            x, y, width, height = self.bbox(time)
            return Rectangle(
                width+2*dpos, height+2*dpos, x-dpos, y-dpos, rx=rx, ry=ry, creation=time,
                fill_opacity=0, stroke_opacity=1, stroke='#ff0', stroke_width=2
            )
        else:
            rect = Rectangle(width=0, height=0, rx=rx, ry=ry, creation=time,
                             fill_opacity=0, stroke_opacity=1, stroke='#ff0', stroke_width=2)
            rect.x.set_onward(time, lambda t: self.bbox(t)[0] - dpos)
            rect.y.set_onward(time, lambda t: self.bbox(t)[1] - dpos)
            rect.width.set_onward(time, lambda t: self.bbox(t)[2] + 2*dpos)
            rect.height.set_onward(time, lambda t: self.bbox(t)[3] + 2*dpos)
            return rect

    def fadein(self, start=0, end=1, change_existence=True, easing=easings.linear):
        """This object will get to the original opacity at the end starting from none
        The show argument before start will be set to none if change_existence, this is a creating function"""
        # This creates the object, we can thus not see it before this command
        if change_existence:
            self.show.set_onward(0, False)
            self.show.set_onward(start, True)

        end_val = self.styling.opacity.at_time(end)
        self.styling.opacity.set(start, end, lambda t: end_val * easing((t-start)/(end-start)))

    def write(self, start=0, end=1, max_stroke_width=1, change_existence=True, easing=easings.linear, stroke_easing=easings.there_and_back):
        """This object will get to the original fill opacity at the end starting from none
        The stroke width will increase and decrease
        The show argument before start will be set to none if change_existence, this is a creating function"""
        # This creates the object, we can thus not see it before this command
        if change_existence:
            self.show.set_onward(0, False)
            self.show.set_onward(start, True)

        end_val = self.styling.fill_opacity.at_time(end)
        self.styling.fill_opacity.set(start, end, lambda t: end_val * easing((t-start)/(end-start)))

        # Increase and decrease the stroke_width for a look at me affect
        sw = self.styling.stroke_width.at_time(end)
        # self.styling.stroke_width.set(start, end, lambda t: max_stroke_width*4*(0.5-abs(linear()(t)-.5))**2 + linear()(t) * sw)
        # self.styling.stroke_width.set(start, end, lambda t: max_stroke_width*4*(0.5-abs(easing((t-start)/(end-start))-.5))**2 + easing((t-start)/(end-start)) * sw)
        s, e = start, end
        self.styling.stroke_width.set(s, e, lambda t: max_stroke_width * stroke_easing((t-s)/(e-s)) + easing((t-s)/(e-s)) * sw)

    def create(self, start=0, end=1, change_existence=True, easing=easings.smooth):
        """Creation argument, draw the path, then do a fade in
        NOTE: add the returned object to the canvas"""
        # NOTE: TODO: creation, simplify and rewrite
        # This creates the object, we can thus not see it before this command
        if change_existence:
            self.show.set_onward(0, False)
            self.show.set_onward(end, True)

        p = morphing.Path(self.path(start))

        def sample(path, t):
            """Sample a path a time 0<=t<=1 based on amount of curves"""
            tot_secs = len(path)
            time = t * tot_secs
            segs = []
            idx = 0
            while time >= 1:
                segs.append(path[idx])
                time -= 1
                idx += 1
            segs.append(path[idx].split(time)[0])
            return morphing.Path(*segs)

        def sample2(path, t):
            """Sample a path a time 0<=t<=1 based on length of the curve"""
            tot_length = path.length()
            length_to_draw = t * tot_length
            segs = []
            idx = 0
            while length_to_draw > 0:
                s = path[idx]
                l = s.length()
                if l <= length_to_draw:
                    segs.append(s)
                    length_to_draw -= l
                else:
                    # Split the segment at the length
                    segs.append(s.split(length_to_draw / l)[0])
                    length_to_draw = 0
                idx += 1
            return morphing.Path(*segs)

        assert callable(easing)
        def f(t): return easing((t-start)/(end-start))

        res = Path('')
        res.d.set(start, end, lambda t: sample2(p, f(t)).d())
        res.styling = self.styling
        res.styling.fill_opacity.set_onward(0, 0)
        res.styling.stroke.set_onward(0, 'green')
        res.styling.stroke_width.set_onward(0, 10)
        if change_existence:
            res.show.set_onward(0, False)
            res.show.set_onward(start, True)
        print('NOTE: Creating an object is under development')
        return res


class Polygon(VObject):
    def __init__(self, *vertices, z=0, creation=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        # The vertices are automatically closed
        self.vertices = [attributes.Coor(creation, v) for v in vertices]
        # The styling arguments
        self.styling = style.Styling(styling_kwargs, creation=creation, fill_opacity=0.7, stroke='#fff', stroke_width=2)

    @property
    def last_change(self):
        return max(max(v.last_change for v in self.vertices), self.z.last_change, self.styling.last_change, self.show.last_change)

    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        if end_time == None:  # We do not animate this movement
            for v in self.vertices:
                v.add_onward(start_time, (dx, dy))
        else:
            raise NotImplementedError('Animation for shifting a Polygon is not yet implemented')
        return self

    def path(self, time):
        vert = [v.at_time(time) for v in self.vertices]
        path = f'M {vert[0][0]},{vert[0][1]}'
        for x, y in vert:
            path += f' L {x},{y}'
        path += ' Z'
        return path

    def to_svg(self, time):
        string = '<polygon'
        # We need to define the points of the Polygon
        points = [v.at_time(time) for v in self.vertices]
        string += f" points='{' '.join(f'{x},{y}' for x, y in points)}'"
        # Add the style
        string += self.styling.svg_style(time)
        # End the object
        string += ' />'
        return string


class FixedVertexPolygon(VObject):
    """The vertices are fixed in time and cannot change"""
    def __init__(self, *vertices, z=0, creation=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.creation = creation
        # The vertices are automatically closed
        self.vertices = vertices
        self.vertex_string = f" points='{' '.join(f'{x},{y}' for x, y in vertices)}'"
        # The styling arguments
        self.styling = style.Styling(styling_kwargs, creation=creation, fill_opacity=0.7, stroke='#fff', stroke_width=2)

    @property
    def last_change(self):
        return max(self.creation, self.styling.last_change, self.z.last_change, self.show.last_change)

    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        raise NotImplementedError('Shifting a Fixed Polygon is not implemented')

    def path(self, time):
        raise NotImplementedError('Retrieving the path of a Fixed Polygon is not implemented')

    def to_svg(self, time):
        string = '<polygon'
        # We need to define the points of the Polygon
        string += self.vertex_string
        # Add the style
        string += self.styling.svg_style(time)
        # End the object
        string += ' />'
        return string


class Circle(VObject):
    def __init__(self, r=100, cx=500, cy=500, z=0, creation=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        # Load the values to initalize the shape
        self.c = attributes.Coor(creation, (cx, cy))
        self.r = attributes.Real(creation, r)
        # The styling arguments
        self.styling = style.Styling(styling_kwargs, creation=creation, fill='#e07a5f', fill_opacity=0.7, stroke='#e07a5f', stroke_width=5)

    @property
    def last_change(self):
        return max(self.c.last_change, self.r.last_change, self.styling.last_change, self.z.last_change, self.show.last_change)

    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        if end_time == None:  # We do not animate this movement
            self.c.add_onward(start_time, (dx, dy))
        else:
            assert callable(easing)
            s, e = start_time, end_time
            self.c.add_onward(s, lambda t: (dx * easing((t-s) / (e-s)), dy * easing((t-s) / (e-s))), last_change=e)
        return self

    def path(self, time):
        # SEE: https://github.com/alexk111/SVG-Morpheus/blob/master/source/js/svg-morpheus.js line 1131
        r = self.r.at_time(time)
        cx, cy = self.c.at_time(time)
        path = f'M{cx-r},{cy}a{r},{r} 0 1,0 {r*2},0a{r},{r} 0 1,0 -{r*2},0z';
        return path

    def to_svg(self, time):
        string = '<circle'
        # We need to define the points of the Polygon
        string += f" cx='{self.c.at_time(time)[0]}'"
        string += f" cy='{self.c.at_time(time)[1]}'"
        string += f" r='{self.r.at_time(time)}'"
        # Add the style
        string += self.styling.svg_style(time)
        # End the object
        string += ' />'
        return string


class Dot(Circle):
    """Returns a point (a small circle with different default styling)"""
    # NOTE: TODO convert Dot into Circle with different default styling arguments
    def __init__(self, r=6, cx=500, cy=500, z=0, creation=0, **styling_kwargs):
        new_style = {'fill': '#83C167', 'fill_opacity': 0.7, 'stroke_width': 0} | styling_kwargs
        super().__init__(r=r, cx=cx, cy=cy, z=z, creation=creation, **new_style)

class Rectangle(VObject):
    def __init__(self, width, height, x=500, y=500, rx=0, ry=0, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        # Load the values to initalize the shape
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.width = attributes.Real(creation, width)
        self.height = attributes.Real(creation, height)
        # Define the rounding of the corners
        self.rx = attributes.Real(creation, rx)
        self.ry = attributes.Real(creation, ry)
        # The styling arguments
        self.styling = style.Styling(styling_kwargs, creation=creation, fill_opacity=0.7, stroke='#fff', stroke_width=3)

    @property
    def last_change(self):
        return max(self.x.last_change, self.y.last_change, self.width.last_change,
                   self.height.last_change, self.rx.last_change, self.ry.last_change,
                   self.styling.last_change, self.z.last_change, self.show.last_change)

    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        if end_time == None:  # We do not animate this movement
            self.x.add_onward(start_time, dx)
            self.y.add_onward(start_time, dy)
        else:
            assert callable(easing)
            s, e = start_time, end_time
            self.x.add_onward(s, lambda t: dx * easing((t-s) / (e-s)), last_change=e)
            self.y.add_onward(s, lambda t: dy * easing((t-s) / (e-s)), last_change=e)
        return self

    def path(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        # SEE: https://github.com/alexk111/SVG-Morpheus/blob/master/source/js/svg-morpheus.js lines 1147-1159
        if rx == 0 and ry == 0:
            path = f'M{x},{y}l{w},0l0,{h}l-{w},0z';
        else:
            # raise NotImplementedError('See below')
            path = f'M{x+rx},{y} l {w-rx*2},0 ' \
                   f'a {rx},{ry} 0 0,1 {rx},{ry} l 0,{h-ry*2} ' \
                   f'a {rx},{ry} 0 0,1 -{rx},{ry} l {rx*2-w},0 ' \
                   f'a {rx},{ry} 0 0,1 -{rx},-{ry} l 0,{ry*2-h} ' \
                   f'a {rx},{ry} 0 0,1 {rx},-{ry} z'
        return path

    def to_svg(self, time):
        string = '<rect'
        # We need to define the points of the Polygon
        string += f" x='{self.x.at_time(time)}'"
        string += f" y='{self.y.at_time(time)}'"
        string += f" width='{self.width.at_time(time)}'"
        string += f" height='{self.height.at_time(time)}'"
        string += f" rx='{self.rx.at_time(time)}'"
        string += f" ry='{self.ry.at_time(time)}'"
        # Add the style
        string += self.styling.svg_style(time)
        # End the object
        string += ' />'
        return string


class EquilateralTriangle(Polygon):
    # NOTE: TODO: ADD ROTATION OPTION
    def __init__(self, side_length, angle=0, cx=500, cy=500, creation=0, z=0, **styling_kwargs):
        """The center is the center of mass at 1/3 the height of the triangle"""
        s = side_length
        h = math.sqrt(3)/2 * s
        vertices = [(cx-s/2, cy+h/3), (cx+s/2, cy+h/3), (cx, cy-2*h/3)]
        def rotate(origin, point, angle):
            """Rotate a point counterclockwise by a given angle around a given origin."""
            ox, oy = origin
            px, py = point
            qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
            qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
            return qx, qy
        midpoint = (sum(v[0] for v in vertices)/3, sum(v[1] for v in vertices)/3)
        vertices = [rotate(midpoint, v, angle*math.pi/180) for v in vertices]
        super().__init__(*vertices, creation=creation, z=z, **styling_kwargs)


class Line(VObject):
    def __init__(self, x1=0, y1=0, x2=100, y2=100, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        # Load the values to initalize the shape
        self.p1 = attributes.Coor(creation, (x1, y1))
        self.p2 = attributes.Coor(creation, (x2, y2))
        # The styling arguments
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff', stroke_width=3)

    @property
    def last_change(self):
        return max(self.p1.last_change, self.p2.last_change, self.styling.last_change, self.z.last_change, self.show.last_change)

    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        if end_time == None:  # We do not animate this movement
            self.p1.add_onward(start_time, (dx, dy))
            self.p2.add_onward(start_time, (dx, dy))
        else:
            assert callable(easing)
            s, e = start_time, end_time
            self.p1.add_onward(s, lambda t: (dx * easing((t-s)/(e-s)), dy * easing((t-s)/(e-s))), last_change=e)
            self.p2.add_onward(s, lambda t: (dx * easing((t-s)/(e-s)), dy * easing((t-s)/(e-s))), last_change=e)
        return self

    def path(self, time):
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return f'M{x1},{y1}L{x2},{y2}Z'

    def to_svg(self, time):
        string = '<line'
        # We need to define the points of the Polygon
        string += f" x1='{self.p1.at_time(time)[0]}'"
        string += f" y1='{self.p1.at_time(time)[1]}'"
        string += f" x2='{self.p2.at_time(time)[0]}'"
        string += f" y2='{self.p2.at_time(time)[1]}'"
        # Add the style
        string += self.styling.svg_style(time)
        # End the object
        string += ' />'
        return string


class Lines(VObject):
    def __init__(self, *vertices, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.vertices = [attributes.Coor(creation, v) for v in vertices]
        # The styling arguments
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff', stroke_width=3)

    @property
    def last_change(self):
        return max(max(v.last_change for v in self.vertices), self.styling.last_change, self.z.last_change, self.show.last_change)

    def to_svg(self, time):
        string = '<polyline'
        # We need to define the points of the Polygon
        points = [v.at_time(time) for v in self.vertices]
        string += f" points='{' '.join(f'{x},{y}' for x, y in points)}'"
        # Add the style
        string += self.styling.svg_style(time)
        # End the object
        string += ' />'
        return string


class Trace(VObject):
    """Folows the point every dt and converts to lines (every dt time)"""
    def __init__(self, point, start=0, end=None, dt=1/60, z=0, **styling_kwargs):
        super().__init__(creation=start, z=z)
        # Load the values to initalize the shape
        self.start = start
        self.end = end
        self.dt = dt
        self.p = point
        # The styling arguments
        self.styling = style.Styling(styling_kwargs, creation=start, stroke='#fff', stroke_width=3)
        self.vert_cache = []
        self.vert_string_cache = ''
        self.vert_string_positions = [-1]

    @property
    def last_change(self):
        return max(self.p.last_change, self.styling.last_change, self.z.last_change, self.show.last_change)

    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        raise NotImplementedError('Shifting a Trace object is not implemented.')

    def path(self, time):
        raise NotImplementedError('Retrieving the path of a Trace object is not implemented.')
        # x1, y1 = self.p1.at_time(time)
        # x2, y2 = self.p2.at_time(time)
        # return f'M{x1},{y1}L{x2},{y2}Z'

    def vertices(self, time):
        """Get the vertices of this path following the point
        i.e. this is equal to the positions of this point spaced dt apart"""
        t = self.start
        end = self.end
        if end == None:  # Indefinite trace, forever
            end = time
        end = min(end, time)
        steps = int((end-t)/self.dt)
        # Add from cache
        vert = self.vert_cache[:steps]
        l = len(vert)
        t += l * self.dt
        done_something = False
        for _ in range(steps - l):
            tmp = self.p.at_time(t)
            vert.append(tmp)
            t += self.dt
            done_something = True
        # Update cache, but only if new values are found
        if done_something:
            self.vert_cache = vert
            for x, y in vert[l:]:
                tmp = f'{x},{y}'
                self.vert_string_cache += tmp + ' '
                self.vert_string_positions.append(self.vert_string_positions[-1] + len(tmp)+1)
        return vert

    def to_svg(self, time):
        string = '<polyline'
        self.vertices(time)  # Set cache values
        end = min(self.end, time) if self.end != None else time
        steps = int((end - self.start)/self.dt)
        if steps == 0:
            return ''
        point_str = self.vert_string_cache[:self.vert_string_positions[steps]]
        current_pos = self.p.at_time(time)
        string += f" points='{point_str} {current_pos[0]},{current_pos[1]}'"
        # Add the style
        string += self.styling.svg_style(time)
        # End the object
        string += ' />'
        return string

    def to_polygon(self, time, fixed=True):
        """We convert this trace into a polygon"""
        if fixed:  # For render speed
            return FixedVertexPolygon(*self.vertices(time), creation=time, z=self.z.at_time(time), **self.styling.kwargs())
        else:
            return Polygon(*self.vertices(time), creation=time, z=self.z.at_time(time), **self.styling.kwargs())

class VCollection:
    """This is the motherclass for all vector objects
    Since an image is not a vector object this will not be a child
    (thus the fadein function and fadeout function will not be the
     same as for vector objects)
    """
    def __init__(self, *objects, creation=0, z=0):
        self.objects = list(objects)
        # If we need to show the entire group
        self.show = attributes.Real(creation, True)
        # Set the draw order
        self.z = attributes.Real(creation, z)

    @property
    def last_change(self):
        return max(max(obj.last_change for obj in self.objects), self.z.last_change, self.show.last_change)

    def __iter__(self):
        return iter(self.objects)

    def to_svg(self, time):
        # We encapsulate all objects into a g object
        string = '<g'
        string += '>\n'
        # Sorting based on the z property/draw order
        lst = []
        for obj in self.objects:
            if obj.show.at_time(time):
                if not hasattr(obj, 'z'):
                    lst.append((0, obj))
                else:
                    lst.append((obj.z.at_time(time), obj))

        # Add the objects
        for _, obj in sorted(lst, key=lambda x: x[0]):
            string += obj.to_svg(time)
            string += '\n'
        string += '</g>'

        return string

    def bbox(self, time, start_idx=0, end_idx=None):
        """Get the bounding box (x, y, width, height of the collection),
        no end_idx means all objects starting from start_idx"""
        if end_idx == None:
            end_idx = len(self.objects)
        obj_box = self.objects[start_idx].bbox(time)
        xmin, ymin = obj_box[0], obj_box[1]
        xmax, ymax = obj_box[2]+xmin, obj_box[3]+ymin
        for obj in self.objects[start_idx+1:end_idx]:
            obj_box = obj.bbox(time)
            xmin = min(xmin, obj_box[0])
            ymin = min(ymin, obj_box[1])
            xmax = max(xmax, obj_box[2]+obj_box[0])
            ymax = max(ymax, obj_box[3]+obj_box[1])
        return (xmin, ymin, xmax-xmin, ymax-ymin)

    def brect(self, time, start_idx=0, end_idx=None, rx=0, ry=0, dpos=5, follow=True):
        """Gets the bounding rectangle (or surrounding rectangle)
        Adjusted with dpos outward, no ending index means all objects"""
        if end_idx == None:
            end_idx = len(self.objects)

        if not follow:  # Get the bounding rectangle once
            x, y, width, height = self.bbox(time, start_idx, end_idx)
            return Rectangle(
                width+2*dpos, height+2*dpos, x-dpos, y-dpos, rx=rx, ry=ry,
                fill_opacity=0, stroke_opacity=1, stroke='#ff0', stroke_width=2
            )
        else:
            rect = Rectangle(width=0, height=0, rx=rx, ry=ry,
                             fill_opacity=0, stroke_opacity=1, stroke='#ff0', stroke_width=2)
            rect.x.set_onward(time, lambda t: self.bbox(t, start_idx, end_idx)[0]-dpos)
            rect.y.set_onward(time, lambda t: self.bbox(t, start_idx, end_idx)[1]-dpos)
            rect.width.set_onward(time, lambda t: self.bbox(t, start_idx, end_idx)[2]+2*dpos)
            rect.height.set_onward(time, lambda t: self.bbox(t, start_idx, end_idx)[3]+2*dpos)
            return rect

    def center_to_pos(self, posx=500, posy=500, start_time=0, end_time=None, easing=easings.smooth):
        """Shifts the center to pos, and animates this from start_time to end_time
        Shifting is done with respect to the position at start_time."""
        xmin, ymin, width, height = self.bbox(start_time)
        dx, dy = posx-(xmin+width/2), posy-(ymin+height/2)
        self.shift(dx=dx, dy=dy, start_time=start_time, end_time=end_time, easing=easing)

    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        """Shift all objects"""
        for obj in self.objects:
            obj.shift(dx=dx, dy=dy, start_time=start_time, end_time=end_time, easing=easing)

    def fadein(self, **kwargs):
        """Fade in the group of VObjects"""
        for obj in self.objects:
            obj.fadein(**kwargs)

    def write(self, start, end, processing=10, max_stroke_width=1/2, change_existence=True):
        """Write the group of VObjects with a sliding window at a time"""
        # Define the seconds per char
        spc = (end-start) / (len(self.objects) + processing)
        # Write all the objects in the sliding window
        for num, obj in enumerate(self.objects):
            obj.write(start=start+spc*num, end=start+spc*(num+processing+1), max_stroke_width=max_stroke_width, change_existence=change_existence)


class MorphObject(VCollection):
    """This morphes one object into the other with a starting time and ending time, this, itself, is an object
    this also needs to be added to the canvas."""
    def __init__(self, morph_from, morph_to, start=0, end=1, z=0, easing=easings.smooth, change_existence=True):
        # Both morph_from and morph_to are converted to collections
        if isinstance(morph_from, VObject):
            morph_from = VCollection(morph_from)
        if isinstance(morph_to, VObject):
            morph_to = VCollection(morph_to)
        assert isinstance(morph_from, VCollection)
        assert isinstance(morph_to, VCollection)

        # This is a converting object, the starting object is not visible during or after the transformation
        # and the ending object is not visible before or during the conversion. If change_existency is True
        # we enforce these existences on the objects.
        if change_existence:
            for obj in morph_from:
                # This is a destruction object for morph_from
                obj.show.set_onward(start, False)
            for obj in morph_to:
                # This is a creation object for morph_to
                obj.show.set_onward(0, False)
                obj.show.set_onward(end, True)

        # Get the starting paths of all objects
        paths_from = [(morphing.Path(obj.path(start)), obj.styling) for obj in morph_from]
        paths_to = [(morphing.Path(obj.path(end)), obj.styling) for obj in morph_to]
        # Get the objects in theoretical paths which be need to convert/morph
        obj_from = morphing.Paths(*paths_from)
        obj_to = morphing.Paths(*paths_to)

        # NOTE: TODO: add transforms, i.e. adjusted paths and rotations
        mapping = obj_from.morph(obj_to, start_time=start, end_time=end, easing=easings.smooth)

        # We now initialize the parent with objects we get from the mapping
        # First we need to convert the mapping into an array of displayable objects.
        objects = []
        for path_specifyer, styling_from, styling_to in mapping:
            new = Path('', x=0, y=0, creation=start, z=z)
            # We need to destroy this morphing object after the animation ended
            new.show.set_onward(end, False)
            # Set the path_specifyer of the path object to equal the mapping
            # Note that the returned specifyer must be remapped from 0<=t<=1 to start<=t<=end
            def f(specifyer):
                return lambda t: specifyer((t-start)/(end-start))
            new.d.set(start, end, f(path_specifyer))
            # We must now set the styling arguments between start and end, morphing styling_from to styling_to
            # But we cannot alter any object from either of the stylings as that would change stylings in other
            # objects as well.
            new.styling = styling_from.interpolate(styling_to, start, end, easing=easing)
            # Add as an object to the collection (of subpaths)
            objects.append(new)

        # Initialize a collection of these objects
        super().__init__(*objects, creation=start, z=z)
        # Discard the entire collection
        self.show.set_onward(end, False)

# :::MARKER: Optimisation/rewrite of code ended here
# NOTE: TODO: add z-coordinates / draw order, argument
# NOTE: TODO: remember, z coordinate as argument + in last_change

class TexObject(VCollection):
    def __init__(self, to_render, x=0, y=0, width=None, creation=0, **styles):
        # NOTE: only one of (width, height), scale can be defined
        # NOTE: make a wildcard VObject that's just an svg for reading other svgs, etc
        # Get the characters and parse them as VObjects
        tex_dir = f'{save_directory}/tex'
        self.char_viewbox, chars = get_characters(tex_dir, to_render, 'latex', '')
        st = {'stroke_width': 0, 'fill': '#fff'} | styles
        # st = style.Styling(styles, fill='#fff', fill_opacity=1, stroke_width=1, stroke='#fff').kwargs()
        chars = [from_svg(char, **st) for char in chars]

        # Init the collection of VObjects
        super().__init__(*chars, creation=creation)

        # Initialize the position and scale/width of the group viewbox
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)

        # Get the bounding box and reset the position
        xmin, ymin, _, _ = self.bbox(creation)
        for obj in self.objects:
            obj.styling.dx.add_onward(creation, lambda t: self.x.at_time(t) - xmin)
            obj.styling.dy.add_onward(creation, lambda t: self.y.at_time(t) - ymin)


class Path(VObject):
    """Similar to a svg path"""
    def __init__(self, path, x=0, y=0, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        # Load the values to initalize the shape
        self.d = attributes.String(creation, path)
        # The styling arguments
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff')
        # Add the position as the transform translate argument after the scale
        self.styling.dx.add_onward(creation, lambda t: x * self.styling.scale_x.at_time(t))
        self.styling.dy.add_onward(creation, lambda t: y * self.styling.scale_y.at_time(t))

    @property
    def last_change(self):
        return max(self.d.last_change, self.styling.last_change, self.z.last_change, self.show.last_change)

    def shift(self, dx=0, dy=0, start_time=0, end_time=None, easing=easings.smooth):
        """Shift the object dx and dy (by changing the transformation styling)"""
        if end_time == None:  # We do not animate this movement
            self.styling.dx.add_onward(start_time, dx)
            self.styling.dy.add_onward(start_time, dy)
        else:
            raise NotImplementedError('Animation for shift not implemented, get smoothing function here')
        return self

    def path(self, time):
        return self.d.at_time(time)

    def to_svg(self, time):
        string = '<path'
        # We need to define the points of the Polygon
        string += f" d='{self.d.at_time(time)}'"
        # Add the style
        string += self.styling.svg_style(time)
        # End the object
        string += ' />'
        return string


def from_svg(specifyer, **styles):
    """Go from bs4 to VObject"""
    if specifyer.name == 'path':
        path = specifyer['d']
        del specifyer['d']
        specifyer['x'] = float(specifyer['x'])
        specifyer['y'] = float(specifyer['y'])
        return Path(path, **(styles | specifyer.attrs))
    elif specifyer.name == 'rect':
        width = float(specifyer['width'])
        height = float(specifyer['height'])
        del specifyer['width']
        del specifyer['height']
        specifyer['x'] = float(specifyer['x'])
        specifyer['y'] = float(specifyer['y'])
        return Path(Rectangle(width, height, x=0, y=0).path(0), **(styles | specifyer.attrs))
        # print(Rectangle(width, height, x=0, y=0).path(0))
        return Rectangle(width, height, **(styles | specifyer.attrs))
    else:
        raise NotImplementedError(f'Type "{specifyer.name}" has no from_svg implemented')


# NOTE: TODO: add speed up buttons and FPS info, etc
# NOTE: TODO: end_time = 0 signifies a single picture
# NOTE: TODO: make a split-tex object that returns multiple vcollections and is thus easier for the MOVING FRAME BOX EXAMPLE
# NOTE: TODO: Update attributes functionalities
# NOTE: TODO: Write to png and mp4 and separate svgs
# NOTE: TODO: Make text object
# NOTE: TODO: Make image object
# NOTE: TODO: Add arc in morphing file
# NOTE: TODO: Restructure files
# NOTE: TODO: Morph with rotate
# NOTE: TODO: Implement create, draw path elements and apply filling.
# NOTE: TODO: add ellipse
# NOTE: TODO: check on other svg objects
# NOTE: add documentation on styling arguments SEE: 'PRESENTATION ATTRIBUTES': https://developer.mozilla.org/en-US/docs/Web/SVG/Element/polygon
# NOTE: TODO: ADD MORE STYLES / PRESENTATION ATTRIBUTES SEE: https://developer.mozilla.org/en-US/docs/Web/SVG/Element/polygon
# NOTE: TODO: add more checks to the code
# NOTE: TODO: add keys like 1,2,3,4,5,6,7,8,9 that signify a time in the view (as percentage or so)
# NOTE: TODO: enable hot-reload on saving the file in the window
# NOTE: TODO: let the user specify easing functions for move_to, shift, etc...
# NOTE: TODO: enable x,y or coordinate setting (also as attribute)
# NOTE: TODO: Correct bounding boxes for transformations (including rotation) -> in morphing
# NOTE: TODO: Coordinates to complex values?
# NOTE: TODO: brect is very slow with latex and follow=True, because of bbox and all its rotations? in that case maybe temporarily store the bbox until a change is made to the object? Or can other optimisations be made in e.g. calculating the box or defining the functions that go with it (maybe on function returning two functions or so is faster).
# NOTE: TODO: VCollection make assertion that it is an iterable of VObject
# NOTE: TODO: Enable preprocessing so that fps is exactly as specified -> already call frame contructions
# NOTE: TODO: EXAMPLE MOVING FRAME BOX with scale_x and scale_y and center_to_pos causes rectangles in tex to move somewhere else
# NOTE: TODO: Add copy functions
# NOTE: TODO: fix the attributes
# NOTE: TODO: write svgs to folder with pause metadata
# NOTE: TODO: pause with slide numbering
# NOTE: TODO: start and end consistently
# NOTE: TODO: round values pushed to svg for compression of data
# NOTE: TODO: compress the folder of svgs created and unfold in run-time
# NOTE: TODO: when using pauses and "slides" get function to export first slide of animation to a more normal-human-readable format
# NOTE: TODO: make a minimal SVGViewer without the toolbars etc., just the keyboard functions.
