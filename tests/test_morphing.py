"""Tests for vectormation.morphing: segment conversion, bezier morphing, path alignment."""
import pytest
import svgpathtools
from vectormation.morphing import (
    CubicBezier, QuadraticBezier, Path, Paths,
    convert_to_bezier,
)
import vectormation.style as style
import vectormation.easings as easings


class TestConvertToBezier:
    def test_line_to_cubic(self):
        seg = svgpathtools.Line(start=0+0j, end=100+100j)
        result = convert_to_bezier(seg)
        assert len(result) == 1
        assert isinstance(result[0], CubicBezier)
        assert result[0].start == pytest.approx(0+0j)
        assert result[0].end == pytest.approx(100+100j)

    def test_cubic_bezier_passthrough(self):
        seg = svgpathtools.CubicBezier(0+0j, 30+50j, 70+50j, 100+0j)
        result = convert_to_bezier(seg)
        assert len(result) == 1
        assert isinstance(result[0], CubicBezier)
        assert result[0].start == pytest.approx(0+0j)
        assert result[0].end == pytest.approx(100+0j)

    def test_quadratic_bezier(self):
        seg = svgpathtools.QuadraticBezier(0+0j, 50+100j, 100+0j)
        result = convert_to_bezier(seg)
        assert len(result) == 1
        assert isinstance(result[0], CubicBezier)

    def test_arc_to_multiple_cubics(self):
        seg = svgpathtools.Arc(0+0j, 50+50j, 0, 0, 1, 100+0j)
        result = convert_to_bezier(seg)
        assert len(result) >= 1
        assert all(isinstance(r, CubicBezier) for r in result)


class TestSegmentToBezier:
    def test_line_to_bezier(self):
        seg = svgpathtools.Line(start=0+0j, end=100+0j)
        result = convert_to_bezier(seg)
        assert len(result) == 1
        b = result[0]
        assert isinstance(b, CubicBezier)
        assert b.start == 0+0j
        assert b.end == 100+0j

    def test_quadratic_to_cubic(self):
        q = QuadraticBezier(start=0+0j, control=50+100j, end=100+0j)
        b = q.to_bezier()
        assert isinstance(b, CubicBezier)
        assert b.start == pytest.approx(0+0j)
        assert b.end == pytest.approx(100+0j)

class TestBezierMorph:
    def test_morph_at_zero_gives_source(self):
        src = CubicBezier(0+0j, 10+10j, 90+10j, 100+0j)
        dst = CubicBezier(0+0j, 10+90j, 90+90j, 100+0j)
        morph_func = src.bezier_morph(dst, easing=easings.linear)
        result = morph_func(0)
        assert result.start == pytest.approx(src.start)
        assert result.end == pytest.approx(src.end)

    def test_morph_at_one_gives_target(self):
        src = CubicBezier(0+0j, 10+10j, 90+10j, 100+0j)
        dst = CubicBezier(0+0j, 10+90j, 90+90j, 100+0j)
        morph_func = src.bezier_morph(dst, easing=easings.linear)
        result = morph_func(1)
        assert result.start == pytest.approx(dst.start)
        assert result.end == pytest.approx(dst.end)


class TestPath:
    def test_adjusted_bbox_no_transforms(self):
        p = Path(svgpathtools.Line(0+0j, 100+100j))
        bbox = p.adjusted_bbox('')
        xmin, xmax, ymin, ymax = bbox
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(100)

    def test_adjusted_path_translate(self):
        p = Path(svgpathtools.Line(0+0j, 100+0j))
        p2 = p.adjusted_path('translate(50,0)')
        bbox = p2.bbox()
        xmin, xmax, ymin, ymax = bbox
        assert xmin == pytest.approx(50)
        assert xmax == pytest.approx(150)


class TestPaths:
    def test_init_with_path_pairs(self):
        s = style.Styling({}, creation=0)
        p = Path(svgpathtools.Line(0+0j, 100+0j))
        paths = Paths((p, s))
        assert len(paths.paths) == 1
        assert len(paths.stylings) == 1

    def test_morph_returns_functions(self):
        s1 = style.Styling({}, creation=0)
        s2 = style.Styling({}, creation=0)
        p1 = Path(svgpathtools.Line(0+0j, 100+0j))
        p2 = Path(svgpathtools.Line(0+0j, 0+100j))
        paths_from = Paths((p1, s1))
        paths_to = Paths((p2, s2))
        result = paths_from.morph(paths_to, start=0, end=1)
        assert len(result) >= 1
        # Each element is (path_func, style_from, style_to, group_from)
        for path_func, sf, st, gf in result:
            assert callable(path_func)


