"""Tests for VectorMathAnim canvas: rendering, camera, object management."""
import os
import re
import tempfile
import pytest

from vectormation._canvas import VectorMathAnim
from vectormation._shapes import Circle, Rectangle, Line
from vectormation._constants import CANVAS_WIDTH, CANVAS_HEIGHT
import vectormation.easings as easings


@pytest.fixture
def canvas():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield VectorMathAnim(tmpdir)


class TestCanvasBasics:

    def test_default_dimensions(self, canvas):
        assert canvas.width == CANVAS_WIDTH
        assert canvas.height == CANVAS_HEIGHT

    def test_viewbox_initial(self, canvas):
        vb = canvas.viewbox
        assert vb == (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    def test_add_and_remove_objects(self, canvas):
        c = Circle(r=50)
        canvas.add_objects(c)
        assert id(c) in canvas.objects
        canvas.remove(c)
        assert id(c) not in canvas.objects

    def test_clear_removes_all(self, canvas):
        canvas.add_objects(Circle(r=50), Rectangle(100, 50))
        canvas.clear()
        assert canvas.get_all_objects() == []

    def test_find_by_type(self, canvas):
        c1 = Circle(r=50)
        c2 = Circle(r=30)
        r = Rectangle(100, 50)
        canvas.add_objects(c1, c2, r)
        circles = canvas.find_by_type(Circle)
        assert len(circles) == 2
        rects = canvas.find_by_type(Rectangle)
        assert len(rects) == 1


class TestFrameGeneration:

    def test_generates_valid_svg(self, canvas):
        canvas.add_objects(Circle(r=50, cx=100, cy=100))
        svg = canvas.generate_frame_svg(0)
        assert svg.startswith("<?xml")
        assert '<svg' in svg
        assert '</svg>' in svg

    def test_viewbox_in_svg(self, canvas):
        svg = canvas.generate_frame_svg(0)
        assert f"viewBox='0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}'" in svg

    def test_invisible_objects_excluded(self, canvas):
        c = Circle(r=50, cx=100, cy=100)
        c.show.set_onward(0, False)
        canvas.add_objects(c)
        svg = canvas.generate_frame_svg(0)
        assert '<ellipse' not in svg

    def test_z_order_sorting(self, canvas):
        """Objects with lower z should appear first in SVG output."""
        front = Circle(r=50, cx=100, cy=100, z=10)
        back = Circle(r=50, cx=200, cy=100, z=-10)
        canvas.add_objects(front, back)
        svg = canvas.generate_frame_svg(0)
        # back (z=-10) should come before front (z=10)
        back_pos = svg.find("cx='200'")
        front_pos = svg.find("cx='100'")
        assert back_pos < front_pos

    def test_objects_rendered_at_correct_time(self, canvas):
        c = Circle(r=50, cx=0, cy=0)
        c.shift(dx=500, dy=0, start=0, end=1, easing=easings.linear)
        canvas.add_objects(c)
        svg_start = canvas.generate_frame_svg(0)
        svg_mid = canvas.generate_frame_svg(0.5)
        svg_end = canvas.generate_frame_svg(1)
        # Extract cx values
        def extract_cx(svg):
            m = re.search(r"cx='([^']+)'", svg)
            return float(m.group(1))
        assert extract_cx(svg_start) == pytest.approx(0, abs=1)
        assert extract_cx(svg_mid) == pytest.approx(250, abs=5)
        assert extract_cx(svg_end) == pytest.approx(500, abs=1)

    def test_write_frame_creates_file(self, canvas):
        canvas.add_objects(Circle(r=50))
        canvas.write_frame(0)
        assert os.path.exists(canvas.filename)
        with open(canvas.filename) as f:
            content = f.read()
        assert '<svg' in content


class TestCamera:

    def test_camera_shift(self, canvas):
        canvas.camera_shift(100, 50, start=0, end=1, easing=easings.linear)
        # At t=0.5, viewbox should be shifted by half
        vb_x = canvas.vb_x.at_time(0.5)
        vb_y = canvas.vb_y.at_time(0.5)
        assert vb_x == pytest.approx(50, abs=2)
        assert vb_y == pytest.approx(25, abs=2)

    def test_camera_zoom_in(self, canvas):
        canvas.camera_zoom(2, start=0, end=0, easing=easings.linear)
        # After 2x zoom, viewbox should be half the size
        vb_w = canvas.vb_w.at_time(0)
        vb_h = canvas.vb_h.at_time(0)
        assert vb_w == pytest.approx(CANVAS_WIDTH / 2)
        assert vb_h == pytest.approx(CANVAS_HEIGHT / 2)

    def test_camera_zoom_out(self, canvas):
        canvas.camera_zoom(0.5, start=0, end=0, easing=easings.linear)
        vb_w = canvas.vb_w.at_time(0)
        assert vb_w > CANVAS_WIDTH  # zoomed out = larger viewbox

    def test_camera_reset(self, canvas):
        canvas.camera_zoom(2, start=0, end=0)
        canvas.camera_reset(start=0, end=0)
        assert canvas.vb_w.at_time(0) == pytest.approx(CANVAS_WIDTH)
        assert canvas.vb_h.at_time(0) == pytest.approx(CANVAS_HEIGHT)

    def test_camera_follow(self, canvas):
        # Zoom in first so camera has room to pan
        canvas.camera_zoom(2, start=0, end=0)
        c = Circle(r=50, cx=CANVAS_WIDTH // 2, cy=CANVAS_HEIGHT // 2)
        c.shift(dx=400, dy=0, start=0, end=1, easing=easings.linear)
        canvas.add_objects(c)
        canvas.camera_follow(c, start=0)
        # With zoomed-in viewbox (half canvas), camera should track
        vb_x_0 = canvas.vb_x.at_time(0)
        vb_x_1 = canvas.vb_x.at_time(1)
        assert vb_x_1 > vb_x_0

    def test_camera_zoom_zero_duration(self, canvas):
        canvas.camera_shift(100, 0, start=0, end=0)
        # Zero duration returns self without error
        assert canvas.vb_x.at_time(0) == pytest.approx(0)  # no shift applied


class TestBackground:

    def test_set_background(self, canvas):
        canvas.set_background(fill='#000')
        assert canvas.background is not None
        svg = canvas.generate_frame_svg(0)
        assert '<rect' in svg

    def test_background_grid(self, canvas):
        canvas.set_background(fill='#000', grid=True, grid_spacing=100)
        svg = canvas.generate_frame_svg(0)
        assert '<line' in svg
