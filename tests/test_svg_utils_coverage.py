"""Extended coverage tests for _svg_utils.py: boolean ops, filters."""
from vectormation.objects import (
    Circle,
    Union, Intersection,
)
from vectormation._svg_utils import ClipPath, BlurFilter, DropShadowFilter


# ── Boolean operations: bbox ──────────────────────────────────────────

class TestBooleanOpsBbox:
    def test_union_bbox(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=200, cy=100)
        u = Union(a, b)
        _, _, w, h = u.bbox(0)
        assert w > 0 and h > 0

    def test_intersection_bbox(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=130, cy=100)
        i = Intersection(a, b)
        _, _, w, h = i.bbox(0)
        assert w > 0 and h > 0


# ── Filter references ─────────────────────────────────────────────────

class TestBlurFilter:
    def test_filter_ref(self):
        f = BlurFilter(std_deviation=4)
        ref = f.filter_ref()
        assert 'url(#' in ref


class TestDropShadowFilter:
    def test_filter_ref(self):
        f = DropShadowFilter()
        ref = f.filter_ref()
        assert 'url(#' in ref


# ── ClipPath ──────────────────────────────────────────────────────────

class TestClipPath:
    def test_unique_id(self):
        cp1 = ClipPath(Circle(r=50, cx=100, cy=100))
        cp2 = ClipPath(Circle(r=30, cx=200, cy=200))
        assert cp1.id != cp2.id
