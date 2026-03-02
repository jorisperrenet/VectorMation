"""Tests for TexCountAnimation, add_label, add_background, match_width/height,
place_between, animate_to, move_towards, snap_to_grid, parallax, and other misc methods."""
from vectormation.objects import (
    Circle, Square, Dot, VectorMathAnim,
    CountAnimation,
)


# -- CountAnimation extras --

class TestCountAnimationExtras:
    def test_count_to(self):
        ca = CountAnimation(start_val=0, end_val=10, start=0, end=1)
        ca.count_to(50, start=1, end=2)
        assert ca._last_val == 50

    def test_renders_at_different_times(self):
        ca = CountAnimation(start_val=0, end_val=100, start=0, end=2)
        v = VectorMathAnim('/tmp')
        v.add(ca)
        svg0 = v.generate_frame_svg(0)
        svg2 = v.generate_frame_svg(2)
        assert '0' in svg0
        assert '100' in svg2


# -- add_label --

class TestAddLabel:
    def test_returns_vcollection(self):
        c = Circle(r=30, cx=500, cy=500)
        labeled = c.add_label('Test')
        assert len(labeled.objects) == 2  # circle + label

    def test_label_text_appears(self):
        c = Circle(r=30, cx=500, cy=500)
        labeled = c.add_label('Hello')
        v = VectorMathAnim('/tmp')
        v.add(labeled)
        svg = v.generate_frame_svg(0)
        assert 'Hello' in svg


# -- add_background --

class TestAddBackground:
    def test_custom_color(self):
        c = Circle(r=30, cx=500, cy=500)
        bg = c.add_background(color='#ff0000')
        v = VectorMathAnim('/tmp')
        v.add(bg)
        svg = v.generate_frame_svg(0)
        assert 'rgb(255,0,0)' in svg

    def test_custom_padding(self):
        c = Circle(r=30, cx=500, cy=500)
        bg1 = c.add_background(padding=10)
        bg2 = c.add_background(padding=50)
        assert bg2.get_width(0) > bg1.get_width(0)


# -- match_width / match_height --

class TestMatchDimensions:
    def test_match_width(self):
        s1 = Square(50, x=100, y=100)
        s2 = Square(200, x=400, y=400)
        s1.match_width(s2)
        assert abs(s1.get_width(0) - s2.get_width(0)) < 2

    def test_match_height(self):
        s1 = Square(50, x=100, y=100)
        s2 = Square(200, x=400, y=400)
        s1.match_height(s2)
        assert abs(s1.get_height(0) - s2.get_height(0)) < 2


# -- place_between --

class TestPlaceBetween:
    def test_centers_between_objects(self):
        a = Dot(cx=100, cy=500)
        b = Dot(cx=900, cy=500)
        d = Dot(cx=0, cy=0)
        d.place_between(a, b, start=0)
        cx, cy = d.center(0)
        assert abs(cx - 500) < 10
        assert abs(cy - 500) < 10

    def test_custom_fraction(self):
        a = Dot(cx=100, cy=500)
        b = Dot(cx=500, cy=500)
        d = Dot(cx=0, cy=0)
        d.place_between(a, b, fraction=0.25, start=0)
        cx, _ = d.center(0)
        assert abs(cx - 200) < 10  # 25% of the way from a to b


# -- animate_to --

class TestAnimateTo:
    def test_moves_to_target(self):
        c = Circle(r=30, cx=100, cy=100)
        target = Circle(r=30, cx=500, cy=500)
        c.animate_to(target, start=0, end=1)
        cx, cy = c.center(1)
        assert abs(cx - 500) < 10
        assert abs(cy - 500) < 10


# -- move_towards --

class TestMoveTowards:
    def test_moves_fraction(self):
        a = Dot(cx=100, cy=100)
        b = Dot(cx=500, cy=100)
        a.move_towards(b, fraction=0.5, start=0)
        cx, _ = a.center(0)
        assert abs(cx - 300) < 10


# -- snap_to_grid --

class TestSnapToGrid:
    def test_snaps_position(self):
        d = Dot(cx=115, cy=225)
        d.snap_to_grid(start=0, end=1, grid_size=100)
        cx, cy = d.center(1)
        assert abs(cx - 100) < 5
        assert abs(cy - 200) < 5


# -- parallax --

class TestParallax:
    def test_moves_by_depth_fraction(self):
        c = Circle(r=30, cx=100, cy=100)
        c.parallax(dx=200, dy=0, start=0, end=1, depth_factor=0.5)
        cx, _ = c.center(1)
        assert abs(cx - 200) < 10  # 100 + 200*0.5


# -- visibility_toggle --

class TestVisibilityToggle:
    def test_toggles(self):
        c = Circle(r=30, cx=500, cy=500)
        c.visibility_toggle(0, 1, 2)
        v = VectorMathAnim('/tmp')
        v.add(c)
        svg_visible = v.generate_frame_svg(0)
        svg_hidden = v.generate_frame_svg(0.5)
        assert len(svg_visible) >= len(svg_hidden)


# -- animate_style --

class TestAnimateStyle:
    def test_stroke_width_changes(self):
        c = Circle(r=30, cx=500, cy=500, stroke_width=2)
        c.animate_style(0, 1, stroke_width=10)
        v = VectorMathAnim('/tmp')
        v.add(c)
        svg_after = v.generate_frame_svg(1)
        assert '10' in svg_after


# -- set_backstroke --

class TestSetBackstroke:
    def test_adds_paint_order(self):
        c = Circle(r=30, cx=500, cy=500)
        c.set_backstroke('#000000', width=10)
        v = VectorMathAnim('/tmp')
        v.add(c)
        svg = v.generate_frame_svg(0)
        assert 'paint-order' in svg


# -- follow_spline --

class TestFollowSpline:
    def test_moves_to_end(self):
        d = Dot(cx=100, cy=100)
        d.follow_spline([(100, 100), (500, 500), (900, 100)], start=0, end=1)
        cx, cy = d.center(1)
        assert abs(cx - 900) < 20
        assert abs(cy - 100) < 20


# -- appear_from --

class TestAppearFrom:
    def test_at_end_reaches_target(self):
        c = Circle(r=30, cx=500, cy=500)
        src = Dot(cx=100, cy=100)
        c.appear_from(src, start=0, end=1)
        cx, cy = c.center(1)
        assert abs(cx - 500) < 10
        assert abs(cy - 500) < 10
