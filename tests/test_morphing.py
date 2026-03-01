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
        xmin, xmax, _, _ = bbox
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(100)

    def test_adjusted_path_translate(self):
        p = Path(svgpathtools.Line(0+0j, 100+0j))
        p2 = p.adjusted_path('translate(50,0)')
        bbox = p2.bbox()
        xmin, xmax, _, _ = bbox
        assert xmin == pytest.approx(50)
        assert xmax == pytest.approx(150)

    def test_adjusted_path_scale(self):
        p = Path(svgpathtools.Line(0+0j, 100+0j))
        p2 = p.adjusted_path('scale(2)')
        bbox = p2.bbox()
        xmin, xmax, _, _ = bbox
        assert xmin == pytest.approx(0)
        assert xmax == pytest.approx(200)

    def test_adjusted_path_multiple_transforms(self):
        p = Path(svgpathtools.Line(0+0j, 100+0j))
        p2 = p.adjusted_path('translate(10,0)', 'scale(2)')
        bbox = p2.bbox()
        # SVG applies transforms right-to-left: scale first, then translate
        xmin, xmax, _, _ = bbox
        assert xmin == pytest.approx(10)
        assert xmax == pytest.approx(210)

    def test_adjusted_bbox_with_scale(self):
        p = Path(svgpathtools.Line(0+0j, 50+50j))
        bbox = p.adjusted_bbox('scale(2)')
        _, xmax, _, ymax = bbox
        assert xmax == pytest.approx(100)
        assert ymax == pytest.approx(100)

    def test_invalid_transform_raises(self):
        p = Path(svgpathtools.Line(0+0j, 100+0j))
        with pytest.raises(ValueError):
            p.adjusted_path('invalid')


class TestBezierMorphInterpolation:
    def test_morph_midpoint_interpolation(self):
        src = CubicBezier(0+0j, 0+0j, 100+0j, 100+0j)
        dst = CubicBezier(0+100j, 0+100j, 100+100j, 100+100j)
        morph_func = src.bezier_morph(dst, easing=easings.linear)
        mid = morph_func(0.5)
        assert mid.start == pytest.approx(0+50j, abs=1)
        assert mid.end == pytest.approx(100+50j, abs=1)

    def test_morph_with_smooth_easing(self):
        src = CubicBezier(0+0j, 25+25j, 75+25j, 100+0j)
        dst = CubicBezier(0+0j, 25+75j, 75+75j, 100+0j)
        morph_func = src.bezier_morph(dst, easing=easings.smooth)
        # At t=0, should be src; at t=1, should be dst
        result_0 = morph_func(0)
        assert result_0.start == pytest.approx(src.start)
        result_1 = morph_func(1)
        assert result_1.end == pytest.approx(dst.end)

    def test_morph_same_bezier(self):
        src = CubicBezier(10+20j, 30+40j, 50+60j, 70+80j)
        morph_func = src.bezier_morph(src, easing=easings.linear)
        result = morph_func(0.5)
        assert result.start == pytest.approx(src.start)
        assert result.end == pytest.approx(src.end)


class TestUnsupportedSegment:
    def test_unsupported_type_raises(self):
        with pytest.raises(TypeError, match='Unsupported segment type'):
            convert_to_bezier("not_a_segment")


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

    def test_morph_unequal_path_counts(self):
        s = style.Styling({}, creation=0)
        p1 = Path(svgpathtools.Line(0+0j, 100+0j))
        p2 = Path(svgpathtools.Line(0+0j, 0+100j))
        p3 = Path(svgpathtools.Line(50+0j, 50+100j))
        paths_from = Paths((p1, s), (p2, s))
        paths_to = Paths((p3, s))
        result = paths_from.morph(paths_to, start=0, end=1)
        assert len(result) >= 1

    def test_morph_path_func_returns_string(self):
        s1 = style.Styling({}, creation=0)
        s2 = style.Styling({}, creation=0)
        p1 = Path(svgpathtools.Line(0+0j, 100+0j))
        p2 = Path(svgpathtools.Line(0+0j, 0+100j))
        paths_from = Paths((p1, s1))
        paths_to = Paths((p2, s2))
        result = paths_from.morph(paths_to, start=0, end=1)
        # The path_func at t=0 should return a valid SVG path string
        d = result[0][0](0)
        assert isinstance(d, str)
        assert d.startswith(('M', 'C'))

    def test_morph_prepare_caches(self):
        s = style.Styling({}, creation=0)
        p1 = Path(svgpathtools.Line(0+0j, 100+0j))
        p2 = Path(svgpathtools.Line(0+0j, 0+100j))
        paths_from = Paths((p1, s))
        paths_to = Paths((p2, s))
        # First call creates subpath_segment_pairs
        paths_from._morph_prepare(paths_to, start=0, end=1)
        assert hasattr(paths_from, 'subpath_segment_pairs')
        # Second morph call should use cached data
        result = paths_from.morph(paths_to, start=0, end=1)
        assert len(result) >= 1


