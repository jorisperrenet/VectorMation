"""Tests for _axes_ext features: annotations, labels, asymptotes, error bars, etc."""
import math
import pytest
from vectormation.objects import Axes, VectorMathAnim, VCollection


@pytest.fixture
def ax():
    return Axes(x_range=(-5, 5), y_range=(-5, 5))


@pytest.fixture
def canvas():
    return VectorMathAnim('/tmp')


# ── add_title ────────────────────────────────────────────────────────

class TestAddTitle:
    def test_returns_text(self, ax, canvas):
        canvas.add(ax)
        t = ax.add_title('My Plot')
        svg = canvas.generate_frame_svg(time=0)
        assert 'My Plot' in svg

    def test_custom_font_size(self, ax, canvas):
        canvas.add(ax)
        t = ax.add_title('Title', font_size=48)
        assert t is not None


# ── add_text_annotation ──────────────────────────────────────────────

class TestAddTextAnnotation:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        group = ax.add_text_annotation(0, 0, 'Origin')
        assert group is not None
        svg = canvas.generate_frame_svg(time=0)
        assert 'Origin' in svg

    def test_custom_offset(self, ax, canvas):
        canvas.add(ax)
        group = ax.add_text_annotation(2, 3, 'Point', dx=60, dy=-60)
        assert group is not None


# ── add_horizontal_label / add_vertical_label ────────────────────────

class TestLabels:
    def test_horizontal_label_right(self, ax, canvas):
        canvas.add(ax)
        lbl = ax.add_horizontal_label(2, 'y=2')
        svg = canvas.generate_frame_svg(time=0)
        assert 'y=2' in svg

    def test_horizontal_label_left(self, ax, canvas):
        canvas.add(ax)
        lbl = ax.add_horizontal_label(-1, 'left', side='left')
        assert lbl is not None

    def test_vertical_label_bottom(self, ax, canvas):
        canvas.add(ax)
        lbl = ax.add_vertical_label(3, 'x=3')
        svg = canvas.generate_frame_svg(time=0)
        assert 'x=3' in svg

    def test_vertical_label_top(self, ax, canvas):
        canvas.add(ax)
        lbl = ax.add_vertical_label(0, 'top', side='top')
        assert lbl is not None


# ── get_horizontal_line / get_dashed_line ────────────────────────────

class TestHelperLines:
    def test_get_horizontal_line(self, ax, canvas):
        canvas.add(ax)
        line = ax.get_horizontal_line(3, 2)
        assert line is not None
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg

    def test_get_dashed_line(self, ax, canvas):
        canvas.add(ax)
        line = ax.get_dashed_line(0, 0, 3, 4)
        assert line is not None
        svg = canvas.generate_frame_svg(time=0)
        assert 'stroke-dasharray' in svg


# ── add_asymptote ────────────────────────────────────────────────────

class TestAsymptote:
    def test_vertical_asymptote(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_asymptote(2, direction='vertical')
        assert line is not None
        svg = canvas.generate_frame_svg(time=0)
        assert 'stroke-dasharray' in svg

    def test_horizontal_asymptote(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_asymptote(3, direction='horizontal')
        assert line is not None

    def test_add_vertical_asymptote_shortcut(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_vertical_asymptote(1)
        assert line is not None

    def test_add_horizontal_asymptote_shortcut(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_horizontal_asymptote(-2)
        assert line is not None


# ── add_horizontal_line / add_vertical_line (guide lines) ────────────

class TestGuideLines:
    def test_horizontal_guide(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_horizontal_line(2)
        assert line is not None

    def test_vertical_guide(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_vertical_line(1)
        assert line is not None

    def test_horizontal_with_animation(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_horizontal_line(0, start=0, end=1)
        assert line is not None

    def test_vertical_with_animation(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_vertical_line(0, start=0.5, end=1.5)
        assert line is not None


# ── add_min_max_labels ───────────────────────────────────────────────

class TestMinMaxLabels:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        labels = ax.add_min_max_labels(lambda x: -(x - 1)**2 + 3, x_range=(-3, 4))
        assert isinstance(labels, VCollection)

    def test_sin_has_extrema(self, ax, canvas):
        canvas.add(ax)
        labels = ax.add_min_max_labels(math.sin, x_range=(-4, 4))
        assert labels is not None


# ── add_error_bars ───────────────────────────────────────────────────

class TestErrorBars:
    def test_uniform_error(self, ax, canvas):
        canvas.add(ax)
        bars = ax.add_error_bars([1, 2, 3], [2, 4, 3], 0.5)
        assert isinstance(bars, VCollection)
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg

    def test_per_point_error(self, ax, canvas):
        canvas.add(ax)
        bars = ax.add_error_bars([1, 2, 3], [2, 4, 3], [0.3, 0.5, 0.2])
        assert isinstance(bars, VCollection)

    def test_single_point(self, ax, canvas):
        canvas.add(ax)
        bars = ax.add_error_bars([0], [0], 1.0)
        assert isinstance(bars, VCollection)


# ── add_regression_line ──────────────────────────────────────────────

class TestRegressionLine:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_regression_line([1, 2, 3, 4], [2, 4, 5, 8])
        assert line is not None
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg

    def test_perfect_line(self, ax, canvas):
        canvas.add(ax)
        line = ax.add_regression_line([0, 1, 2], [0, 2, 4])
        assert line is not None


# ── coords_label ─────────────────────────────────────────────────────

class TestCoordsLabel:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        lbl = ax.coords_label(2, 3)
        svg = canvas.generate_frame_svg(time=0)
        assert '2' in svg
        assert '3' in svg

    def test_custom_text(self, ax, canvas):
        canvas.add(ax)
        lbl = ax.coords_label(1, 1, text='A(1,1)')
        svg = canvas.generate_frame_svg(time=0)
        assert 'A(1,1)' in svg


# ── add_interval ─────────────────────────────────────────────────────

class TestAddInterval:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        interval = ax.add_interval(-2, 2)
        assert interval is not None
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg or '<path' in svg


# ── get_vertical_lines / get_horizontal_lines ────────────────────────

class TestBulkLines:
    def test_get_vertical_lines(self, ax, canvas):
        canvas.add(ax)
        f = lambda x: x**2
        lines = ax.get_vertical_lines(f, [1, 2, 3])
        assert isinstance(lines, VCollection)
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg

    def test_get_horizontal_lines(self, ax, canvas):
        canvas.add(ax)
        lines = ax.get_horizontal_lines([1, 2, 3])
        assert isinstance(lines, VCollection)


# ── get_tangent_line / get_secant_line ───────────────────────────────

class TestTangentSecant:
    def test_tangent_line(self, ax, canvas):
        canvas.add(ax)
        line = ax.get_tangent_line(math.sin, 0)
        assert line is not None
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg

    def test_secant_line(self, ax, canvas):
        canvas.add(ax)
        line = ax.get_secant_line(math.sin, 0, 1)
        assert line is not None


# ── add_slope_field ──────────────────────────────────────────────────

class TestSlopeField:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        field = ax.add_slope_field(lambda x, y: x - y,
                                   x_step=1, y_step=1)
        assert isinstance(field, VCollection)
        svg = canvas.generate_frame_svg(time=0)
        assert '<line' in svg

    def test_with_div_by_zero_slope(self, ax, canvas):
        """Slope field should skip points that raise."""
        canvas.add(ax)
        field = ax.add_slope_field(lambda x, y: 1 / y if y != 0 else 1e10,
                                   x_step=2, y_step=2)
        assert isinstance(field, VCollection)


# ── plot_vector_field ────────────────────────────────────────────────

class TestVectorField:
    def test_circular_field(self, ax, canvas):
        canvas.add(ax)
        vf = ax.plot_vector_field(lambda x, y: (-y, x),
                                   x_step=2, y_step=2)
        assert isinstance(vf, VCollection)

    def test_gradient_field(self, ax, canvas):
        canvas.add(ax)
        vf = ax.plot_vector_field(lambda x, y: (x, y),
                                   x_step=2, y_step=2)
        assert isinstance(vf, VCollection)


# ── get_slope_field (alternate method) ───────────────────────────────

class TestGetSlopeField:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        field = ax.get_slope_field(lambda x, y: y - x,
                                   x_step=2, y_step=2)
        assert isinstance(field, VCollection)


# ── get_riemann_rectangles ───────────────────────────────────────────

class TestRiemannRectangles:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        rects = ax.get_riemann_rectangles(lambda x: x**2, x_range=(0, 3), dx=0.5)
        assert rects is not None
        svg = canvas.generate_frame_svg(time=0)
        assert '<rect' in svg or '<path' in svg

    def test_fine_resolution(self, ax, canvas):
        canvas.add(ax)
        rects = ax.get_riemann_rectangles(math.sin, x_range=(0, math.pi), dx=0.1)
        assert rects is not None


# ── add_cursor / add_trace ───────────────────────────────────────────

class TestCursorTrace:
    def test_add_cursor(self, ax, canvas):
        canvas.add(ax)
        cursor = ax.add_cursor(math.sin, -3, 3, start=0, end=2)
        assert cursor is not None

    def test_add_trace(self, ax, canvas):
        canvas.add(ax)
        trace = ax.add_trace(math.sin, -3, 3, start=0, end=2)
        assert trace is not None


# ── add_vector ───────────────────────────────────────────────────────

class TestAddVector:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        arrow = ax.add_vector(3, 2)
        assert arrow is not None
        svg = canvas.generate_frame_svg(time=0)
        assert 'polygon' in svg.lower() or 'path' in svg.lower() or 'line' in svg.lower()

    def test_from_custom_origin(self, ax, canvas):
        canvas.add(ax)
        arrow = ax.add_vector(1, 1, origin_x=2, origin_y=2)
        assert arrow is not None


# ── add_arrow_annotation ─────────────────────────────────────────────

class TestArrowAnnotation:
    def test_basic(self, ax, canvas):
        canvas.add(ax)
        ann = ax.add_arrow_annotation(2, 3, 'peak')
        assert ann is not None
        svg = canvas.generate_frame_svg(time=0)
        assert 'peak' in svg

    def test_direction_variants(self, ax, canvas):
        canvas.add(ax)
        for d in ['up', 'down', 'left', 'right']:
            ann = ax.add_arrow_annotation(0, 0, f'dir={d}', direction=d)
            assert ann is not None
