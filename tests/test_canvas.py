"""Tests for VectorMathAnim canvas."""
import os
import tempfile
from vectormation.objects import VectorMathAnim, Circle, Rectangle, ClipPath
from vectormation.colors import LinearGradient


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

    def test_camera_shift(self):
        self.canvas.camera_shift(100, 50, start=0, end=1)
        # At time 1, viewbox x should have shifted by ~100
        vbx = self.canvas.vb_x.at_time(1)
        assert vbx > 50  # Should be close to 100

    def test_camera_shift_returns_self(self):
        result = self.canvas.camera_shift(10, 10, start=0, end=1)
        assert result is self.canvas

    def test_camera_shift_zero_duration(self):
        result = self.canvas.camera_shift(100, 50, start=1, end=1)
        assert result is self.canvas

    def test_camera_zoom_in(self):
        self.canvas.camera_zoom(2, start=0, end=1)
        # After zooming in 2x, width should be half
        vbw = self.canvas.vb_w.at_time(1)
        assert vbw < 800

    def test_camera_zoom_returns_self(self):
        result = self.canvas.camera_zoom(2, start=0, end=1)
        assert result is self.canvas

    def test_camera_follow(self):
        c = Circle(r=50, cx=600, cy=400)
        self.canvas.add_objects(c)
        self.canvas.camera_follow(c, start=0, end=1)
        # Camera should be centered on the circle
        vbx = self.canvas.vb_x.at_time(0.5)
        assert isinstance(vbx, (int, float))

    def test_camera_follow_returns_self(self):
        c = Circle(r=50, cx=100, cy=100)
        result = self.canvas.camera_follow(c, start=0)
        assert result is self.canvas

    def test_camera_reset(self):
        self.canvas.camera_zoom(2, start=0, end=0.5)
        self.canvas.camera_reset(start=0.5, end=1)
        vbw = self.canvas.vb_w.at_time(1)
        assert vbw == 800

    def test_camera_reset_returns_self(self):
        result = self.canvas.camera_reset(start=0, end=1)
        assert result is self.canvas

    def test_remove_and_readd(self):
        c = Circle(r=50)
        self.canvas.add_objects(c)
        assert id(c) in self.canvas.objects
        self.canvas.remove(c)
        assert id(c) not in self.canvas.objects

    def test_default_dimensions(self):
        canvas = VectorMathAnim(self.tmpdir)
        assert canvas.width == 1920
        assert canvas.height == 1080

    def test_multiple_objects_rendering(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(50, 50, x=200, y=200)
        self.canvas.add_objects(c, r)
        svg = self.canvas.generate_frame_svg(0)
        assert '<circle' in svg
        assert '<rect' in svg

    def test_z_ordering(self):
        c1 = Circle(r=50, cx=100, cy=100, z=1)
        c2 = Circle(r=50, cx=100, cy=100, z=0)
        self.canvas.add_objects(c1, c2)
        svg = self.canvas.generate_frame_svg(0)
        # Both circles should be in SVG
        assert svg.count('<circle') == 2

    # ── get_snap_points ────────────────────────────────────────────────

    def test_get_snap_points_empty(self):
        points = self.canvas.get_snap_points(time=0)
        assert points == []

    def test_get_snap_points_with_objects(self):
        c = Circle(r=50, cx=200, cy=300)
        self.canvas.add_objects(c)
        points = self.canvas.get_snap_points(time=0)
        # Circle should contribute snap points (center at minimum)
        assert len(points) > 0

    def test_get_snap_points_default_time(self):
        c = Circle(r=50, cx=200, cy=300)
        self.canvas.add_objects(c)
        points = self.canvas.get_snap_points()
        assert isinstance(points, list)

    # ── export_sections ────────────────────────────────────────────────

    def test_export_sections_no_sections(self):
        c = Circle(r=30, cx=100, cy=100)
        self.canvas.add_objects(c)
        self.canvas.export_sections()
        # Should create at least one file (start time)
        files = [f for f in os.listdir(self.canvas.save_dir) if f.startswith('section_')]
        assert len(files) >= 1

    def test_export_sections_with_sections(self):
        c = Circle(r=30, cx=100, cy=100)
        self.canvas.add_objects(c)
        self.canvas.add_section(1.0)
        self.canvas.add_section(2.0)
        self.canvas.export_sections(prefix='sec')
        files = [f for f in os.listdir(self.canvas.save_dir) if f.startswith('sec_')]
        assert len(files) == 3  # start + 2 sections

    def test_export_sections_custom_prefix(self):
        c = Circle(r=30, cx=100, cy=100)
        self.canvas.add_objects(c)
        self.canvas.export_sections(prefix='frame')
        files = [f for f in os.listdir(self.canvas.save_dir) if f.startswith('frame_')]
        assert len(files) >= 1
        assert files[0].endswith('.svg')


class TestFocusOnEdgeCases:
    def test_no_objects(self):
        """focus_on with no objects should return self without error."""
        canvas = VectorMathAnim(tempfile.mkdtemp())
        result = canvas.focus_on()
        assert result is canvas
