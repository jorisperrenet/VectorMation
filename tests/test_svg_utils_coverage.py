"""Extended coverage tests for _svg_utils.py: boolean ops, filters, ZoomedInset, StreamLines."""
from vectormation.objects import (
    Circle, Rectangle, Dot,
    Union, Difference, Intersection, Exclusion,
    StreamLines, ZoomedInset, VectorMathAnim,
)
from vectormation._svg_utils import ClipPath, BlurFilter, DropShadowFilter


# ── Boolean operations: styling & animation ─────────────────────────────

class TestBooleanOpsStyling:
    def test_union_custom_fill(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        u = Union(a, b, fill='#FF0000', stroke='#00FF00')
        svg = u.to_svg(0)
        assert svg is not None

    def test_difference_custom_fill(self):
        a = Circle(r=60, cx=100, cy=100)
        b = Circle(r=30, cx=120, cy=100)
        d = Difference(a, b, fill='#00FF00')
        svg = d.to_svg(0)
        assert svg is not None

    def test_intersection_custom_fill(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        i = Intersection(a, b, fill='#0000FF')
        svg = i.to_svg(0)
        assert svg is not None

    def test_exclusion_custom_fill(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        e = Exclusion(a, b, fill='#FFFF00')
        svg = e.to_svg(0)
        assert svg is not None


class TestBooleanOpsWithRectangles:
    def test_union_rect_circle(self):
        r = Rectangle(width=100, height=80, x=50, y=50)
        c = Circle(r=40, cx=150, cy=90)
        u = Union(r, c)
        svg = u.to_svg(0)
        assert svg is not None

    def test_difference_rect_circle(self):
        r = Rectangle(width=100, height=80, x=50, y=50)
        c = Circle(r=30, cx=100, cy=90)
        d = Difference(r, c)
        svg = d.to_svg(0)
        assert svg is not None

    def test_intersection_rect_rect(self):
        r1 = Rectangle(width=100, height=100, x=0, y=0)
        r2 = Rectangle(width=100, height=100, x=50, y=50)
        i = Intersection(r1, r2)
        svg = i.to_svg(0)
        assert svg is not None

    def test_exclusion_rect_rect(self):
        r1 = Rectangle(width=100, height=100, x=0, y=0)
        r2 = Rectangle(width=100, height=100, x=50, y=50)
        e = Exclusion(r1, r2)
        svg = e.to_svg(0)
        assert svg is not None


class TestBooleanOpsAnimation:
    def test_union_fadein(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        u = Union(a, b)
        u.fadein(0, 1)
        svg0 = u.to_svg(0)
        svg1 = u.to_svg(1)
        assert svg0 is not None
        assert svg1 is not None

    def test_difference_creation(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=30, cx=120, cy=100)
        d = Difference(a, b, creation=2)
        # Before creation time, opacity is 0 (scale 0,0)
        svg_before = d.to_svg(1)
        svg_after = d.to_svg(3)
        assert svg_after is not None and len(svg_after) > 0


class TestBooleanOpsBbox:
    def test_union_bbox(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=200, cy=100)
        u = Union(a, b)
        x, y, w, h = u.bbox(0)
        assert w > 0 and h > 0

    def test_intersection_bbox(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        i = Intersection(a, b)
        x, y, w, h = i.bbox(0)
        assert w > 0 and h > 0


# ── Filter parameter variations ─────────────────────────────────────────

class TestBlurFilter:
    def test_custom_deviation(self):
        f = BlurFilter(std_deviation=10)
        assert f.std_deviation == 10

    def test_zero_deviation(self):
        f = BlurFilter(std_deviation=0)
        svg = f.to_svg_def()
        assert 'filter' in svg.lower()

    def test_repr(self):
        f = BlurFilter(std_deviation=5)
        r = repr(f)
        assert r is not None

    def test_filter_ref(self):
        f = BlurFilter(std_deviation=4)
        ref = f.filter_ref()
        assert 'url(#' in ref


class TestDropShadowFilter:
    def test_custom_params(self):
        f = DropShadowFilter(dx=10, dy=10, std_deviation=8, color='#FF0000', opacity=0.3)
        assert f.dx == 10
        assert f.dy == 10
        assert f.color == '#FF0000'

    def test_zero_offset(self):
        f = DropShadowFilter(dx=0, dy=0)
        svg = f.to_svg_def()
        assert 'filter' in svg.lower()

    def test_repr(self):
        f = DropShadowFilter()
        r = repr(f)
        assert r is not None

    def test_filter_ref(self):
        f = DropShadowFilter()
        ref = f.filter_ref()
        assert 'url(#' in ref


class TestClipPath:
    def test_with_circle(self):
        c = Circle(r=50, cx=100, cy=100)
        cp = ClipPath(c)
        assert len(cp.objects) == 1

    def test_with_multiple_objects(self):
        c = Circle(r=50, cx=100, cy=100)
        r = Rectangle(width=100, height=100, x=50, y=50)
        cp = ClipPath(c, r)
        assert len(cp.objects) == 2

    def test_unique_id(self):
        cp1 = ClipPath(Circle(r=50, cx=100, cy=100))
        cp2 = ClipPath(Circle(r=30, cx=200, cy=200))
        assert cp1.id != cp2.id


# ── StreamLines extended ────────────────────────────────────────────────

class TestStreamLinesExtended:
    def test_divergent_field(self):
        sl = StreamLines(lambda x, y: (x - 960, y - 540))
        # Should create objects without error
        assert sl is not None

    def test_spiral_field(self):
        sl = StreamLines(lambda x, y: (-(y - 540), x - 960))
        assert sl is not None

    def test_custom_styling(self):
        sl = StreamLines(lambda x, y: (1, 0), stroke='#FF0000', stroke_width=3)
        assert sl is not None


# ── ZoomedInset extended ────────────────────────────────────────────────

class TestZoomedInsetExtended:
    def test_with_objects(self):
        canvas = VectorMathAnim(save_dir='/tmp/test_svg')
        canvas.add(Circle(r=50, cx=100, cy=100, fill='#FF0000'))
        zi = ZoomedInset(canvas, source=(50, 50, 100, 100),
                         display=(500, 200, 300, 300))
        svg = zi.to_svg(0)
        assert svg is not None

    def test_custom_colors(self):
        canvas = VectorMathAnim(save_dir='/tmp/test_svg')
        zi = ZoomedInset(canvas, source=(0, 0, 200, 200),
                         display=(600, 100, 400, 400),
                         frame_color='#FF0000', display_color='#00FF00')
        svg = zi.to_svg(0)
        assert svg is not None

    def test_bbox(self):
        canvas = VectorMathAnim(save_dir='/tmp/test_svg')
        zi = ZoomedInset(canvas, source=(100, 100, 200, 200),
                         display=(500, 200, 300, 300))
        x, y, w, h = zi.bbox(0)
        assert w > 0 and h > 0
