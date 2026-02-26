"""Tests for VectorMathAnim canvas."""
import os
import tempfile
import pytest
from vectormation.objects import VectorMathAnim, Circle, Rectangle, ClipPath
from vectormation.colors import LinearGradient, RadialGradient


class TestCanvas:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.canvas = VectorMathAnim(self.tmpdir, width=800, height=600)

    def test_init(self):
        assert self.canvas.width == 800
        assert self.canvas.height == 600
        assert self.canvas.viewbox == (0, 0, 800, 600)

    def test_add_objects(self):
        c = Circle(r=50)
        self.canvas.add_objects(c)
        assert id(c) in self.canvas.objects

    def test_generate_frame_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        self.canvas.add_objects(c)
        svg = self.canvas.generate_frame_svg(0)
        assert '<?xml' in svg
        assert '<svg' in svg
        assert '<circle' in svg
        assert '</svg>' in svg

    def test_viewbox_in_svg(self):
        svg = self.canvas.generate_frame_svg(0)
        assert "viewBox='0 0 800 600'" in svg

    def test_write_frame(self):
        c = Circle(r=50)
        self.canvas.add_objects(c)
        outfile = os.path.join(self.tmpdir, 'test.svg')
        self.canvas.write_frame(time=0, filename=outfile)
        assert os.path.exists(outfile)
        with open(outfile) as f:
            content = f.read()
        assert '<circle' in content

    def test_set_background(self):
        self.canvas.set_background(fill='#333')
        assert self.canvas.background is not None
        svg = self.canvas.generate_frame_svg(0)
        assert '<rect' in svg

    def test_get_visible_objects_info(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(width=50, height=50, x=200, y=200)
        self.canvas.add_objects(c, r)
        info = self.canvas.get_visible_objects_info(0)
        classes = [item['class'] for item in info]
        assert 'Circle' in classes
        assert 'Rectangle' in classes

    def test_get_visible_excludes_background(self):
        self.canvas.set_background(fill='#333')
        c = Circle(r=50, cx=100, cy=100)
        self.canvas.add_objects(c)
        info = self.canvas.get_visible_objects_info(0)
        classes = [item['class'] for item in info]
        assert 'Circle' in classes
        # Background should be excluded from visible objects info
        assert len(info) == 1

    def test_viewbox_zoom(self):
        self.canvas.handle_browser_event({
            'type': 'zoom', 'factor': 2, 'rel_x': 0.5, 'rel_y': 0.5
        })
        vb = self.canvas.viewbox
        assert vb[2] < 800  # Width should have decreased (zoomed in)

    def test_viewbox_zoom_clamp(self):
        """Zoom out should be clamped at 4x canvas dimensions."""
        self.canvas.handle_browser_event({
            'type': 'zoom', 'factor': 0.01, 'rel_x': 0.5, 'rel_y': 0.5
        })
        vb = self.canvas.viewbox
        assert vb[2] <= self.canvas.width * 4
        assert vb[3] <= self.canvas.height * 4

    def test_set_background_replaces(self):
        self.canvas.set_background(fill='#333')
        bg1 = self.canvas.background
        self.canvas.set_background(fill='#fff')
        bg2 = self.canvas.background
        assert bg1 is not bg2

    def test_add_gradient_and_render(self):
        lg = LinearGradient([('0%', '#f00'), ('100%', '#00f')])
        self.canvas.add_gradient(lg)
        c = Circle(r=50, cx=100, cy=100, fill=lg)
        self.canvas.add_objects(c)
        svg = self.canvas.generate_frame_svg(0)
        assert '<defs>' in svg
        assert '<linearGradient' in svg

    def test_add_clip_path_and_render(self):
        clip_circle = Circle(r=50, cx=100, cy=100)
        cp = ClipPath(clip_circle)
        self.canvas.add_clip_path(cp)
        svg = self.canvas.generate_frame_svg(0)
        assert '<defs>' in svg
        assert '<clipPath' in svg

    def test_add_section(self):
        self.canvas.add_section(1.0)
        self.canvas.add_section(0.5)
        assert self.canvas.sections == [0.5, 1.0]

    def test_handle_fit(self):
        self.canvas.viewbox = (100, 100, 400, 300)
        self.canvas.handle_browser_event({'type': 'control', 'action': 'fit'})
        assert self.canvas.viewbox == (0, 0, 800, 600)
