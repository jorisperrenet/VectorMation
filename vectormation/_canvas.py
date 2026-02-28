"""VectorMathAnim: the main canvas/video object."""
import os
import re
import sys
import logging
import tempfile

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation._constants import CANVAS_WIDTH, CANVAS_HEIGHT
from vectormation._base_helpers import _ramp

logger = logging.getLogger('vectormation')

class VectorMathAnim:
    """Canvas/video where we can ask a frame at a certain time."""
    def __init__(self, save_dir, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, scale=1, verbose=False):
        if verbose:
            logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
        else:
            logging.basicConfig(level=logging.WARNING)

        self.save_dir = save_dir  # Directory to save frames in
        os.makedirs(save_dir, exist_ok=True)
        self.filename = f'{save_dir}/gen.svg'
        self.width = width
        self.height = height
        self.scale = scale
        self.vb_x = attributes.Real(0, 0)
        self.vb_y = attributes.Real(0, 0)
        self.vb_w = attributes.Real(0, width)
        self.vb_h = attributes.Real(0, height)
        self.objects = {}  # {id(object): object}
        self.defs = {}  # {id_str: gradient/clippath object}
        self.time = 0  # Time of the current video
        self.dt = 0
        self.start_anim = None
        self.end_anim = None
        self.animate = None
        self.background = None
        self.sections = []  # List of section end times (sorted)
        self.speed_multiplier = 1.0  # Playback speed multiplier
        self.single_picture = False  # If True, display a single static frame
        self.snap_enabled = False  # If True, send snap points to browser

        logger.info('Initialized canvas %dx%d, saving to %s', width, height, save_dir)

        # We need to set the save directory globally
        global save_directory
        save_directory = save_dir

    def __repr__(self):
        return f'VectorMathAnim({self.width}x{self.height})'

    @property
    def viewbox(self):
        t = self.time
        return (self.vb_x.at_time(t), self.vb_y.at_time(t),
                self.vb_w.at_time(t), self.vb_h.at_time(t))

    @viewbox.setter
    def viewbox(self, value):
        t = self.time
        for attr, val in zip((self.vb_x, self.vb_y, self.vb_w, self.vb_h), value):
            attr.set_onward(t, val)

    def camera_shift(self, dx, dy, start, end, easing=easings.smooth):
        """Pan the camera by (dx, dy) pixels over [start, end]."""
        dur = end - start
        if dur <= 0:
            return self
        self.vb_x.add_onward(start, _ramp(start, dur, dx, easing), last_change=end)
        self.vb_y.add_onward(start, _ramp(start, dur, dy, easing), last_change=end)
        return self

    def _animate_viewbox(self, start, end, x, y, w, h, easing):
        """Animate all four viewbox attributes to new values."""
        self.vb_x.move_to(start, end, x, easing=easing)
        self.vb_y.move_to(start, end, y, easing=easing)
        self.vb_w.move_to(start, end, w, easing=easing)
        self.vb_h.move_to(start, end, h, easing=easing)

    def camera_zoom(self, factor, start, end, cx=None, cy=None, easing=easings.smooth):
        """Zoom the camera by factor around (cx, cy) over [start, end].
        factor > 1 zooms in, factor < 1 zooms out."""
        if cx is None:
            cx = self.width / 2
        if cy is None:
            cy = self.height / 2
        cur_w, cur_h = self.vb_w.at_time(start), self.vb_h.at_time(start)
        new_w, new_h = cur_w / (factor or 1), cur_h / (factor or 1)
        new_x = max(0, min(cx - new_w / 2, self.width - new_w))
        new_y = max(0, min(cy - new_h / 2, self.height - new_h))
        self._animate_viewbox(start, end, new_x, new_y, new_w, new_h, easing)
        return self

    def camera_follow(self, obj, start, end=None):
        """Make the camera center on an object over [start, end]."""
        w, h = self.width, self.height
        def _vb_x(t):
            cx = obj.center(t)[0]
            vw = self.vb_w.at_time(t)
            return max(0, min(cx - vw / 2, w - vw))
        def _vb_y(t):
            cy = obj.center(t)[1]
            vh = self.vb_h.at_time(t)
            return max(0, min(cy - vh / 2, h - vh))
        self.vb_x.set_onward(start, _vb_x)
        self.vb_y.set_onward(start, _vb_y)
        if end is not None:
            self.vb_x.set_onward(end, self.vb_x.at_time(end))
            self.vb_y.set_onward(end, self.vb_y.at_time(end))
        return self

    def camera_reset(self, start, end, easing=easings.smooth):
        """Reset camera to default (full canvas) viewbox over [start, end]."""
        self._animate_viewbox(start, end, 0, 0, self.width, self.height, easing)
        return self

    def focus_on(self, *objects, start, end, padding=100, easing=easings.smooth):
        """Pan and zoom the camera to fit the given objects with padding."""
        from vectormation._base import VCollection
        group = VCollection(*objects) if len(objects) > 1 else objects[0]
        bx, by, bw, bh = group.bbox(start)
        target_x = bx - padding
        target_y = by - padding
        target_w = bw + 2 * padding
        target_h = bh + 2 * padding
        if target_w <= 0 or target_h <= 0:
            return self
        # Maintain aspect ratio
        aspect = self.width / self.height
        if target_w / target_h > aspect:
            target_h = target_w / aspect
            target_y = by + bh / 2 - target_h / 2
        else:
            target_w = target_h * aspect
            target_x = bx + bw / 2 - target_w / 2
        self._animate_viewbox(start, end, target_x, target_y, target_w, target_h, easing)
        return self

    def set_background(self, creation=0, z=-1, grid=False, grid_spacing=60, grid_color='#333', **styling):
        """Sets the background of the animation (otherwise no background is added)."""
        if self.background is not None:
            del self.objects[id(self.background)]
        st = style.Styling(styling, creation=creation, stroke_width=0)
        from vectormation._shapes import Rectangle, Line
        self.background = Rectangle(self.width, self.height, x=0, y=0, rx=0, ry=0, creation=creation, z=z, **st.kwargs())
        self.add_objects(self.background)
        if grid:
            kw = dict(creation=creation, z=z, stroke=grid_color, stroke_width=1)
            gx = 0.0
            while gx <= self.width:
                self.add_objects(Line(x1=gx, y1=0, x2=gx, y2=self.height, **kw))
                gx += grid_spacing
            gy = 0.0
            while gy <= self.height:
                self.add_objects(Line(x1=0, y1=gy, x2=self.width, y2=gy, **kw))
                gy += grid_spacing
        return self

    def add_section(self, time):
        """Add a section break at the given time."""
        self.sections.append(time)
        self.sections.sort()
        return self

    def add_objects(self, *args):
        """Register objects to be displayed."""
        for obj in args:
            self.objects[id(obj)] = obj
        return self

    def remove(self, *args):
        """Remove objects from the canvas."""
        for obj in args:
            self.objects.pop(id(obj), None)
        return self

    def clear(self):
        """Remove all objects from the canvas (keeps background and defs)."""
        bg_id = id(self.background) if self.background else None
        self.objects = {k: v for k, v in self.objects.items() if k == bg_id}
        return self

    def add_def(self, def_obj):
        """Register a gradient or clip path for the <defs> block."""
        self.defs[def_obj.id] = def_obj
        return self

    # Aliases
    def get_all_objects(self):
        """Return a list of all registered objects (excluding background)."""
        bg_id = id(self.background) if self.background else None
        return [v for k, v in self.objects.items() if k != bg_id]

    def find_by_type(self, cls):
        """Return all objects matching the given type (including subclasses)."""
        return [obj for obj in self.get_all_objects() if isinstance(obj, cls)]

    def find(self, predicate):
        """Return all objects where predicate(obj) returns True."""
        return [obj for obj in self.get_all_objects() if predicate(obj)]

    def _visible_objects(self, time=None):
        """Yield non-background objects visible at *time*."""
        if time is None:
            time = 0
        for obj in self.objects.values():
            if obj is not self.background and obj.show.at_time(time):
                yield obj

    def get_object_count(self, time=None):
        """Return the number of visible objects at the given time."""
        return sum(1 for _ in self._visible_objects(time))

    def list_objects_by_type(self, time=None):
        """Return a dict mapping class names to lists of objects of that type."""
        result = {}
        for obj in self._visible_objects(time):
            result.setdefault(type(obj).__name__, []).append(obj)
        return result

    @property
    def duration(self):
        """Return the total animation duration in seconds (auto-detected)."""
        return self._resolve_end(None)

    add = add_objects
    add_gradient = add_def
    add_clip_path = add_def

    def render(self, **kwargs):
        """Convenience alias: opens the animation in the browser viewer."""
        return self.browser_display(**kwargs)

    def get_snap_points(self, time=None):
        """Extract snappable points (vertices, endpoints, centers) from all visible objects."""
        if time is None:
            time = self.time
        points = []
        for obj in self._visible_objects(time):
            self._collect_snap_points(obj, time, points)
        return points

    @classmethod
    def _collect_snap_points(cls, obj, time, points):
        """Recursively collect snap points, descending into VCollections."""
        from vectormation._base import VCollection
        if isinstance(obj, VCollection):
            for sub in obj.objects:
                if hasattr(sub, 'show') and not sub.show.at_time(time):
                    continue
                cls._collect_snap_points(sub, time, points)
        elif hasattr(obj, 'snap_points'):
            points.extend(obj.snap_points(time))

    @staticmethod
    def _round_svg_values(svg, precision=2):
        """Round floating-point numbers in SVG strings for data compression."""
        def _round_match(m):
            return f'{float(m.group()):.{precision}f}'.rstrip('0').rstrip('.')
        return re.sub(r'-?\d+\.\d{3,}', _round_match, svg)

    def generate_frame_svg(self, time=None):
        """Generate the SVG content for a frame as a string."""
        if time is None:
            time = self.time  # The canvas time

        logger.log(5, 'Generating frame at t=%.3f', time)
        parts = []
        parts.append("<?xml version='1.0' encoding='UTF-8'?>\n")
        vb = (self.vb_x.at_time(time), self.vb_y.at_time(time),
              self.vb_w.at_time(time), self.vb_h.at_time(time))
        header = f"<svg version='1.1' xmlns='http://www.w3.org/2000/svg' " \
                 f"xmlns:xlink='http://www.w3.org/1999/xlink' " \
                 f"width='{self.width * self.scale}' height='{self.height * self.scale}' " \
                 f"viewBox='{vb[0]} {vb[1]} {vb[2]} {vb[3]}'>\n"
        parts.append(header)

        # Output <defs> block for gradients and clip paths
        if self.defs:
            parts.append('<defs>\n')
            for def_obj in self.defs.values():
                if hasattr(def_obj, 'to_svg_def'):
                    parts.append(def_obj.to_svg_def(time) + '\n')
            parts.append('</defs>\n')

        # Run updaters and add objects sorted by z-order
        visible = [(obj.z.at_time(time), obj)
                   for obj in self.objects.values() if obj.show.at_time(time)]
        for _, obj in sorted(visible, key=lambda x: x[0]):
            if hasattr(obj, '_run_updaters'):
                obj._run_updaters(time)
            parts.append(obj.to_svg(time) + '\n')

        # Close the header
        parts.append("</svg>")
        svg = ''.join(parts)
        return self._round_svg_values(svg)

    def write_frame(self, time=None, filename=None):
        """This combines all the svgs of objects alive at the canvas time and writes to disk"""
        if filename is None:
            filename = self.filename
        with open(filename, 'w') as s:
            s.write(self.generate_frame_svg(time))

    def handle_browser_event(self, msg):
        """Process a parsed JSON message from the browser viewer."""
        msg_type = msg.get('type')
        if msg_type == 'zoom':
            factor = msg['factor']
            rel_x = max(0, min(1, msg['rel_x']))
            rel_y = max(0, min(1, msg['rel_y']))
            v = self.viewbox
            new_w = min(v[2] / (factor or 1), self.width * 4)
            new_h = min(v[3] / (factor or 1), self.height * 4)
            self.viewbox = (v[0] + rel_x * (v[2] - new_w), v[1] + rel_y * (v[3] - new_h), new_w, new_h)
        elif msg_type == 'control':
            handler = self._control_handlers.get(msg.get('action'))
            if handler:
                handler(self, msg)

    def _handle_quit(self, _msg):
        logger.info('Quitting...')
        sys.exit()

    def _handle_restart(self, _msg):
        self.time = self.start_anim
        self.frame_count = 0

    def _handle_fit(self, _msg):
        self.viewbox = (0, 0, self.width, self.height)

    def _handle_pause(self, _msg):
        self.animate = not self.animate

    def _handle_next_section(self, _msg):
        if not self.animate:
            self.animate = True
        else:
            for t in self.sections:
                if t > self.time + 1e-9:  # type: ignore[operator]
                    self.time = t
                    self._sync_frame_count()
                    self.animate = False
                    break

    def _sync_frame_count(self):
        """Update frame_count from current time."""
        self.frame_count = round((self.time - self.start_anim) / self.dt)  # type: ignore[operator]

    def _handle_step(self, msg, direction=1):
        self.animate = False
        self.time = max(self.start_anim, min(self.time + direction * self.dt, self.end_anim))  # type: ignore[type-var,operator]
        self._sync_frame_count()

    def _handle_speed(self, msg):
        self.speed_multiplier = max(0.1, msg.get('value', 1.0))

    def _handle_snap_toggle(self, _msg):
        self.snap_enabled = not self.snap_enabled

    def _handle_snap_enable(self, _msg):
        self.snap_enabled = True

    def _handle_jump(self, msg):
        pct = max(0.0, min(1.0, msg.get('percentage', 0.0)))
        duration = self.end_anim - self.start_anim  # type: ignore[operator]
        self.time = self.start_anim + pct * duration  # type: ignore[operator]
        self._sync_frame_count()
        logger.info('Jumped to %.0f%%', pct * 100)

    _control_handlers = {
        'quit': _handle_quit, 'restart': _handle_restart,
        'fit': _handle_fit, 'pause': _handle_pause,
        'next_section': _handle_next_section,
        'step_forward': lambda self, msg: self._handle_step(msg, 1),
        'step_backward': lambda self, msg: self._handle_step(msg, -1),
        'speed': _handle_speed,
        'snap_toggle': _handle_snap_toggle, 'snap_enable': _handle_snap_enable,
        'jump': _handle_jump,
    }

    def export_sections(self, prefix='section'):
        """Export each section as a standalone SVG file.
        Writes one SVG per section boundary (plus the start time)."""
        times = [self.start_anim or 0] + self.sections
        for i, t in enumerate(times):
            filename = os.path.join(self.save_dir, f'{prefix}_{i:03d}.svg')
            self.write_frame(time=t, filename=filename)
            logger.info('Exported section %d at t=%.2f to %s', i, t, filename)

    @staticmethod
    def _require_cairosvg():
        """Import and return cairosvg, raising a helpful error if missing."""
        try:
            import cairosvg  # type: ignore[import-not-found]
            return cairosvg
        except ImportError:
            raise ImportError('cairosvg is required for export. Install it with: pip install cairosvg')

    def export_png(self, time=0, filename='frame.png', scale=None):
        """Export a single frame as PNG using cairosvg."""
        cairosvg = self._require_cairosvg()
        scale, ow, oh = self._export_dims(scale)
        svg = self.generate_frame_svg(time)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=filename,
                         output_width=ow, output_height=oh)
        logger.info('Exported PNG to %s', filename)

    def _resolve_end(self, end):
        if end is None:
            candidates = [obj.last_change for obj in self.objects.values()]
            candidates.extend(a.last_change for a in (self.vb_x, self.vb_y, self.vb_w, self.vb_h))
            return max(candidates)
        return end

    def _export_dims(self, scale=None):
        """Return (scale, output_width, output_height) for export methods."""
        scale = scale or self.scale
        return scale, int(self.width * scale), int(self.height * scale)

    def _frame_times(self, start, end, fps):
        """Generate frame timestamps from start to end at given fps."""
        fps = max(fps, 1)
        dt = 1.0 / fps
        t = start
        while t <= end + dt * 0.5:
            yield t
            t += dt

    def export_video(self, filename='animation.mp4', start=0, end=None, fps=60, scale=None):
        """Export animation as video using cairosvg + ffmpeg."""
        import subprocess, shutil
        cairosvg = self._require_cairosvg()
        if shutil.which('ffmpeg') is None:
            raise RuntimeError('ffmpeg is required for video export. Install it from https://ffmpeg.org/')

        end = self._resolve_end(end)
        scale, output_w, output_h = self._export_dims(scale)
        tmpdir = tempfile.mkdtemp(prefix='vectormation_')
        try:
            n_frames = 0
            for i, t in enumerate(self._frame_times(start, end, fps)):
                svg = self.generate_frame_svg(t)
                cairosvg.svg2png(bytestring=svg.encode(),
                                 output_width=output_w, output_height=output_h,
                                 write_to=os.path.join(tmpdir, f'frame_{i:05d}.png'))
                n_frames = i + 1
            subprocess.run([
                'ffmpeg', '-y', '-framerate', str(fps),
                '-i', os.path.join(tmpdir, 'frame_%05d.png'),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', filename
            ], check=True, capture_output=True)
            logger.info('Exported video to %s (%d frames, %dx%d)', filename, n_frames, output_w, output_h)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def export_gif(self, filename='animation.gif', start=0, end=None, fps=30, scale=None, loop=0):
        """Export animation as an animated GIF using cairosvg + Pillow."""
        cairosvg = self._require_cairosvg()
        try:
            from PIL import Image as PILImage  # type: ignore[import-not-found]
        except ImportError:
            raise ImportError('Pillow is required for GIF export. Install it with: pip install Pillow')
        import io

        end = self._resolve_end(end)
        scale, output_w, output_h = self._export_dims(scale)
        frames = []
        for t in self._frame_times(start, end, fps):
            svg = self.generate_frame_svg(t)
            png_data: bytes = cairosvg.svg2png(bytestring=svg.encode(),
                                               output_width=output_w, output_height=output_h)  # type: ignore[assignment]
            rgba = PILImage.open(io.BytesIO(png_data)).convert('RGBA')
            rgb = PILImage.new('RGB', rgba.size, (255, 255, 255))
            rgb.paste(rgba, mask=rgba.split()[3])
            frames.append(rgb)

        if not frames:
            logger.warning('No frames generated for GIF export')
            return

        frames[0].save(filename, save_all=True, append_images=frames[1:],
                       duration=int(1000 / fps), loop=loop, optimize=True)
        logger.info('Exported GIF to %s (%d frames, %dx%d)', filename, len(frames), output_w, output_h)

    def get_visible_objects_info(self, time=None):
        """Return info about visible objects at the given time.
        Returns a list of dicts with 'class' and 'id' keys."""
        if time is None:
            time = self.time
        return [{'class': obj.__class__.__name__, 'id': id(obj)}
                for obj in self._visible_objects(time)]

    def browser_display(self, start=0, end=None, fps=60,
                        port=8765, hot_reload=False):
        """View the animation in a browser via WebSocket.
        If end == 0, displays a single static picture (no animation)."""
        import inspect
        from vectormation.browser import BrowserViewer

        if end == 0:
            # Single picture mode: just display the frame at start
            self.single_picture = True
            end = start
            logger.info('Single picture mode at t=%.2f', start)
        elif end is None:
            end = self._resolve_end(None)
            logger.info('Found that the ending time is %s', end)
        self.end_anim = end
        if start < 0:
            self.start_anim = end + start
        else:
            self.start_anim = start
        self.animate = not self.single_picture
        self.time = start
        self.frame_count = 0
        self.dt = 1 / fps

        logger.info('Starting browser viewer on port %d', port)

        script_path = None
        if hot_reload:
            # Detect the calling script
            frame = inspect.stack()[1]
            script_path = os.path.abspath(frame.filename)

        viewer = BrowserViewer(self, fps=fps, port=port,
                               hot_reload=hot_reload, script_path=script_path)
        viewer.start()

