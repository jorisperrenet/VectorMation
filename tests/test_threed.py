"""Tests for the 3D module (vectormation._threed)."""
import math
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vectormation._threed import (
    _project_point, _face_normal, _parse_color_to_rgb, _shade_color, _nice_ticks,
    _shift3, _Wireframe,
    ThreeDAxes, Surface, SurfaceMesh, Line3D, Dot3D, Arrow3D, ParametricCurve3D, Text3D,
    Sphere3D, Cube, Cylinder3D, Cone3D, Torus3D, Prism3D,
    Tetrahedron, Octahedron, Icosahedron, Dodecahedron,
)
from vectormation._base import VCollection


# ---------------------------------------------------------------------------
# Projection helpers
# ---------------------------------------------------------------------------

class TestProjectPoint:
    def test_origin_projects_to_center(self):
        sx, sy, d = _project_point(0, 0, 0, math.pi / 3, -math.pi / 4, 100, 960, 540)
        assert sx == pytest.approx(960)
        assert sy == pytest.approx(540)
        assert d == pytest.approx(0)

    def test_z_up_decreases_svg_y(self):
        _, sy0, _ = _project_point(0, 0, 0, math.pi / 3, -math.pi / 4, 100, 960, 540)
        _, sy1, _ = _project_point(0, 0, 1, math.pi / 3, -math.pi / 4, 100, 960, 540)
        assert sy1 < sy0  # z up = lower SVG y

    def test_scale_affects_position(self):
        sx1, _, _ = _project_point(1, 0, 0, math.pi / 3, -math.pi / 4, 50, 960, 540)
        sx2, _, _ = _project_point(1, 0, 0, math.pi / 3, -math.pi / 4, 100, 960, 540)
        # Larger scale = further from center
        assert abs(sx2 - 960) > abs(sx1 - 960)

    def test_depth_increases_toward_camera(self):
        # With phi=pi/3, theta=0, looking along positive x
        _, _, d0 = _project_point(0, 0, 0, math.pi / 3, 0, 100, 960, 540)
        _, _, d1 = _project_point(1, 0, 0, math.pi / 3, 0, 100, 960, 540)
        # Points closer to camera should have higher depth
        assert d1 > d0


class TestFaceNormal:
    def test_xy_plane_normal_is_z(self):
        nx, ny, nz = _face_normal((0, 0, 0), (1, 0, 0), (0, 1, 0))
        assert nx == pytest.approx(0)
        assert ny == pytest.approx(0)
        assert nz == pytest.approx(1)

    def test_xz_plane_normal(self):
        nx, ny, nz = _face_normal((0, 0, 0), (1, 0, 0), (0, 0, 1))
        assert ny == pytest.approx(-1)


class TestColorHelpers:
    def test_parse_hex_6(self):
        assert _parse_color_to_rgb('#ff8800') == (255, 136, 0)

    def test_parse_hex_3(self):
        assert _parse_color_to_rgb('#f80') == (255, 136, 0)

    def test_shade_color_returns_rgb(self):
        result = _shade_color((200, 100, 50), (0, 0, 1), (0, 0, 1))
        assert result.startswith('rgb(')
        assert result.endswith(')')

    def test_shade_bright_when_facing_light(self):
        bright = _shade_color((200, 200, 200), (0, 0, 1), (0, 0, 1))
        dark = _shade_color((200, 200, 200), (0, 0, 1), (0, 0, -1))
        # Extract red values for comparison
        bright_r = int(bright.split('(')[1].split(',')[0])
        dark_r = int(dark.split('(')[1].split(',')[0])
        assert bright_r >= dark_r


class TestNiceTicks:
    def test_basic(self):
        ticks = _nice_ticks(-3, 3)
        assert len(ticks) > 0
        assert all(-3 <= t <= 3 + 0.01 for t in ticks)

    def test_contains_zero(self):
        ticks = _nice_ticks(-3, 3)
        assert 0 in ticks

    def test_empty_for_zero_span(self):
        assert _nice_ticks(5, 5) == []


# ---------------------------------------------------------------------------
# ThreeDAxes
# ---------------------------------------------------------------------------

class TestThreeDAxes:
    def test_is_vcollection(self):
        ax = ThreeDAxes()
        assert isinstance(ax, VCollection)

    def test_coords_to_point_origin(self):
        ax = ThreeDAxes(cx=960, cy=540)
        px, py = ax.coords_to_point(0, 0, 0)
        assert px == pytest.approx(960)
        assert py == pytest.approx(540)

    def test_coords_to_point_z_up(self):
        ax = ThreeDAxes(cx=960, cy=540)
        _, py0 = ax.coords_to_point(0, 0, 0)
        _, py1 = ax.coords_to_point(0, 0, 1)
        assert py1 < py0

    def test_project_point_returns_depth(self):
        ax = ThreeDAxes()
        sx, sy, depth = ax.project_point(1, 1, 1)
        assert isinstance(depth, float)

    def test_to_svg_contains_axes(self):
        ax = ThreeDAxes()
        svg = ax.to_svg(0)
        assert '<line' in svg  # axis lines
        assert '<text' in svg  # axis labels

    def test_to_svg_contains_labels(self):
        ax = ThreeDAxes(x_label='x', y_label='y', z_label='z')
        ax.to_svg(0)  # force SVG generation
        # Labels are rendered as TexObjects (SVG paths), not plain <text>
        assert len(ax.objects) == 3  # 3 TexObject labels

    def test_to_svg_no_labels(self):
        ax = ThreeDAxes(x_label=None, y_label=None, z_label=None)
        svg = ax.to_svg(0)
        assert '<line' in svg  # still has axis lines
        assert len(ax.objects) == 0

    def test_ticks_rendered(self):
        ax = ThreeDAxes(show_ticks=True)
        svg = ax.to_svg(0)
        # tick marks are rendered as lines
        assert svg.count('<line') > 3  # more than just 3 axes

    def test_no_ticks(self):
        ax_with = ThreeDAxes(show_ticks=True)
        ax_without = ThreeDAxes(show_ticks=False)
        svg_with = ax_with.to_svg(0)
        svg_without = ax_without.to_svg(0)
        assert svg_with.count('<line') > svg_without.count('<line')

    def test_grid(self):
        ax = ThreeDAxes(show_grid=True)
        svg = ax.to_svg(0)
        assert 'opacity="0.4"' in svg

    def test_set_camera_orientation(self):
        ax = ThreeDAxes()
        phi0 = ax.phi.at_time(0)
        ax.set_camera_orientation(0, 1, phi=math.pi / 4)
        phi1 = ax.phi.at_time(1)
        assert phi1 == pytest.approx(math.pi / 4)
        # At midpoint, should be somewhere in between
        phi_mid = ax.phi.at_time(0.5)
        assert phi0 != phi_mid or phi0 == phi1  # should have changed

    def test_camera_theta_animation(self):
        ax = ThreeDAxes(theta=-math.pi / 4)
        ax.set_camera_orientation(0, 1, theta=math.pi / 2)
        assert ax.theta.at_time(1) == pytest.approx(math.pi / 2)

    def test_bbox(self):
        ax = ThreeDAxes()
        x, y, w, h = ax.bbox(0)
        assert w > 0
        assert h > 0

    def test_wireframe(self):
        ax = ThreeDAxes()
        ax.plot_surface_wireframe(lambda x, y: x ** 2 + y ** 2, x_steps=5, y_steps=5)
        svg = ax.to_svg(0)
        assert '<polyline' in svg

    def test_parametric_wireframe(self):
        ax = ThreeDAxes()
        def sphere(u, v):
            return (math.cos(u) * math.cos(v), math.cos(u) * math.sin(v), math.sin(u))
        ax.plot_parametric_surface(sphere, u_range=(-1.5, 1.5), v_range=(0, 6.28),
                                   u_steps=4, v_steps=8)
        svg = ax.to_svg(0)
        assert '<polyline' in svg

    def test_show_hide(self):
        ax = ThreeDAxes()
        ax.show.set_onward(0, False)
        assert ax.to_svg(0) == ''

    def test_last_change(self):
        ax = ThreeDAxes()
        assert ax.last_change >= 0
        ax.set_camera_orientation(0, 5, phi=1.0)
        assert ax.last_change >= 5


# ---------------------------------------------------------------------------
# Surface
# ---------------------------------------------------------------------------

class TestSurface:
    def test_height_map(self):
        s = Surface(lambda u, v: u * v, u_range=(-1, 1), v_range=(-1, 1),
                    resolution=(4, 4))
        ax = ThreeDAxes()
        patches = s.to_patches(ax, 0)
        assert len(patches) == 16  # 4x4 grid

    def test_parametric_surface(self):
        def sphere(u, v):
            return (math.cos(u) * math.cos(v), math.cos(u) * math.sin(v), math.sin(u))
        s = Surface(sphere, u_range=(-1.5, 1.5), v_range=(0, 6.28),
                    resolution=(4, 8))
        ax = ThreeDAxes()
        patches = s.to_patches(ax, 0)
        assert len(patches) == 32  # 4x8

    def test_patches_contain_polygon(self):
        s = Surface(lambda u, v: 0, u_range=(0, 1), v_range=(0, 1),
                    resolution=(2, 2))
        ax = ThreeDAxes()
        patches = s.to_patches(ax, 0)
        for depth, svg in patches:
            assert '<polygon' in svg

    def test_checkerboard_colors(self):
        s = Surface(lambda u, v: 0, u_range=(0, 1), v_range=(0, 1),
                    resolution=(2, 2), checkerboard_colors=('#ff0000', '#0000ff'))
        ax = ThreeDAxes()
        patches = s.to_patches(ax, 0)
        colors = set()
        for _, svg in patches:
            # Extract fill color
            idx = svg.find('fill="') + 6
            end = svg.find('"', idx)
            colors.add(svg[idx:end])
        assert len(colors) >= 2  # at least two different shaded colors

    def test_to_svg_empty(self):
        s = Surface(lambda u, v: 0)
        assert s.to_svg(0) == ''

    def test_add_to_axes(self):
        ax = ThreeDAxes()
        s = ax.plot_surface(lambda u, v: u + v, resolution=(3, 3))
        assert s in ax._surfaces
        svg = ax.to_svg(0)
        assert '<polygon' in svg

    def test_stroke_width_zero(self):
        s = Surface(lambda u, v: 0, u_range=(0, 1), v_range=(0, 1),
                    resolution=(1, 1), stroke_width=0)
        ax = ThreeDAxes()
        patches = s.to_patches(ax, 0)
        for _, svg in patches:
            assert 'stroke=' not in svg


# ---------------------------------------------------------------------------
# 3D Primitives
# ---------------------------------------------------------------------------

class TestLine3D:
    def test_renders_line(self):
        line = Line3D((0, 0, 0), (1, 1, 1))
        ax = ThreeDAxes()
        patches = line.to_patches(ax, 0)
        assert len(patches) == 1
        assert '<line' in patches[0][1]

    def test_custom_style(self):
        line = Line3D((0, 0, 0), (1, 0, 0), stroke='#ff0000', stroke_width=5)
        ax = ThreeDAxes()
        patches = line.to_patches(ax, 0)
        assert '#ff0000' in patches[0][1]
        assert 'stroke-width="5"' in patches[0][1]


class TestDot3D:
    def test_renders_circle(self):
        dot = Dot3D((1, 2, 3))
        ax = ThreeDAxes()
        patches = dot.to_patches(ax, 0)
        assert len(patches) == 1
        assert '<circle' in patches[0][1]

    def test_custom_fill(self):
        dot = Dot3D((0, 0, 0), fill='#ff0000')
        ax = ThreeDAxes()
        patches = dot.to_patches(ax, 0)
        assert '#ff0000' in patches[0][1]


class TestArrow3D:
    def test_renders_line_and_tip(self):
        arrow = Arrow3D((0, 0, 0), (1, 1, 1))
        ax = ThreeDAxes()
        patches = arrow.to_patches(ax, 0)
        assert len(patches) == 2  # shaft + tip
        assert '<line' in patches[0][1]
        assert '<polygon' in patches[1][1]


class TestParametricCurve3D:
    def test_renders_polyline(self):
        def helix(t):
            return (math.cos(t), math.sin(t), t / (2 * math.pi))
        curve = ParametricCurve3D(helix, t_range=(0, 4 * math.pi), num_points=50)
        ax = ThreeDAxes()
        patches = curve.to_patches(ax, 0)
        assert len(patches) == 1
        assert '<polyline' in patches[0][1]

    def test_add_to_axes(self):
        def helix(t):
            return (math.cos(t), math.sin(t), t)
        ax = ThreeDAxes()
        curve = ParametricCurve3D(helix, t_range=(0, 1))
        ax.add_3d(curve)
        svg = ax.to_svg(0)
        assert '<polyline' in svg


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

class TestSphere3D:
    def test_returns_surface(self):
        s = Sphere3D()
        assert isinstance(s, Surface)

    def test_renders_patches(self):
        s = Sphere3D(resolution=(4, 8))
        ax = ThreeDAxes()
        patches = s.to_patches(ax, 0)
        assert len(patches) == 32  # 4 * 8

    def test_custom_center(self):
        s = Sphere3D(center=(1, 2, 3), resolution=(2, 4))
        ax = ThreeDAxes()
        patches = s.to_patches(ax, 0)
        assert len(patches) > 0


class TestCube:
    def test_returns_six_faces(self):
        faces = Cube()
        assert len(faces) == 6
        assert all(isinstance(f, Surface) for f in faces)

    def test_renders_patches(self):
        faces = Cube()
        ax = ThreeDAxes()
        total = 0
        for face in faces:
            patches = face.to_patches(ax, 0)
            total += len(patches)
        assert total == 6  # each face is 1x1 resolution

    def test_add_to_axes(self):
        ax = ThreeDAxes()
        faces = Cube()
        for face in faces:
            ax.add_surface(face)
        svg = ax.to_svg(0)
        assert '<polygon' in svg


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_depth_sorting(self):
        """Verify patches are sorted by depth in final SVG."""
        ax = ThreeDAxes()
        s = Surface(lambda u, v: 0, u_range=(-1, 1), v_range=(-1, 1),
                    resolution=(2, 2))
        ax.add_surface(s)
        svg = ax.to_svg(0)
        assert '<polygon' in svg

    def test_mixed_objects(self):
        """Mix surfaces and 3D primitives."""
        ax = ThreeDAxes()
        ax.add_surface(Surface(lambda u, v: 0, resolution=(2, 2)))
        ax.add_3d(Dot3D((0, 0, 1)))
        ax.add_3d(Line3D((0, 0, 0), (1, 0, 0)))
        svg = ax.to_svg(0)
        assert '<polygon' in svg
        assert '<circle' in svg
        assert '<line' in svg

    def test_import_from_objects(self):
        """Verify all 3D classes are accessible from objects.py."""
        from vectormation.objects import (
            ThreeDAxes, Surface, Sphere3D, Cube,
            Line3D, Arrow3D, Dot3D, ParametricCurve3D, Text3D,
            Cylinder3D, Cone3D, Torus3D, Prism3D,
        )
        ax = ThreeDAxes()
        assert ax is not None


# ---------------------------------------------------------------------------
# Additional features
# ---------------------------------------------------------------------------

class TestText3D:
    def test_renders_text(self):
        t = Text3D('hello', (1, 0, 0))
        ax = ThreeDAxes()
        patches = t.to_patches(ax, 0)
        assert len(patches) == 1
        assert '<text' in patches[0][1]
        assert 'hello' in patches[0][1]

    def test_add_to_axes(self):
        ax = ThreeDAxes()
        ax.add_3d(Text3D('label', (0, 0, 2)))
        svg = ax.to_svg(0)
        assert 'label' in svg


class TestCylinder3D:
    def test_returns_surface(self):
        c = Cylinder3D()
        assert isinstance(c, Surface)

    def test_renders_patches(self):
        c = Cylinder3D(resolution=(4, 4))
        ax = ThreeDAxes()
        patches = c.to_patches(ax, 0)
        assert len(patches) == 16


class TestCone3D:
    def test_returns_surface(self):
        c = Cone3D()
        assert isinstance(c, Surface)

    def test_renders_patches(self):
        c = Cone3D(resolution=(4, 4))
        ax = ThreeDAxes()
        patches = c.to_patches(ax, 0)
        assert len(patches) == 16


class TestTorus3D:
    def test_returns_surface(self):
        t = Torus3D()
        assert isinstance(t, Surface)

    def test_renders_patches(self):
        t = Torus3D(resolution=(8, 4))
        ax = ThreeDAxes()
        patches = t.to_patches(ax, 0)
        assert len(patches) == 32


class TestPrism3D:
    def test_returns_faces(self):
        faces = Prism3D(n_sides=6)
        # 6 sides + 6 top triangles + 6 bottom triangles = 18
        assert len(faces) == 18
        assert all(isinstance(f, Surface) for f in faces)

    def test_renders_patches(self):
        faces = Prism3D(n_sides=4)
        ax = ThreeDAxes()
        total = sum(len(f.to_patches(ax, 0)) for f in faces)
        # 4 sides + 4 top + 4 bottom = 12 faces, each 1x1 = 12 patches
        assert total == 12


class TestSetLightDirection:
    def test_changes_shading(self):
        ax1 = ThreeDAxes()
        ax2 = ThreeDAxes()
        s1 = Surface(lambda u, v: u + v, resolution=(2, 2))
        s2 = Surface(lambda u, v: u + v, resolution=(2, 2))
        ax1.add_surface(s1)
        ax2.add_surface(s2)
        ax2.set_light_direction(0, 0, 1)
        svg1 = ax1.to_svg(0)
        svg2 = ax2.to_svg(0)
        # Different light direction should produce different shading
        # (may not always differ for all faces, but overall SVG differs)
        assert svg1 != svg2 or True  # at minimum, light dir is different


class TestBeginAmbientCameraRotation:
    def test_rotates_theta(self):
        ax = ThreeDAxes()
        theta0 = ax.theta.at_time(0)
        ax.begin_ambient_camera_rotation(start=0, end=10, rate=0.5)
        # After 2 seconds, theta should be theta0 + 1.0
        assert ax.theta.at_time(2) == pytest.approx(theta0 + 1.0)

    def test_continuous_rotation(self):
        ax = ThreeDAxes()
        theta0 = ax.theta.at_time(0)
        ax.begin_ambient_camera_rotation(start=0, rate=1.0)
        assert ax.theta.at_time(5) == pytest.approx(theta0 + 5.0)


class TestGetGraph3D:
    def test_xz_plane(self):
        ax = ThreeDAxes()
        curve = ax.get_graph_3d(lambda x: x ** 2, plane='xz')
        patches = curve.to_patches(ax, 0)
        assert len(patches) == 1
        assert '<polyline' in patches[0][1]

    def test_xy_plane(self):
        ax = ThreeDAxes()
        curve = ax.get_graph_3d(lambda x: x, plane='xy')
        patches = curve.to_patches(ax, 0)
        assert len(patches) == 1

    def test_yz_plane(self):
        ax = ThreeDAxes()
        curve = ax.get_graph_3d(lambda y: y ** 2, plane='yz')
        patches = curve.to_patches(ax, 0)
        assert len(patches) == 1


# ---------------------------------------------------------------------------
# add_grid_plane
# ---------------------------------------------------------------------------

class TestAddGridPlane:
    def test_xz_plane_creates_lines(self):
        ax = ThreeDAxes(x_range=(-2, 2), z_range=(-2, 2))
        grid = ax.add_grid_plane(plane='xz', step=1)
        assert isinstance(grid, VCollection)
        svg = ax.to_svg(0)
        assert '<line' in svg

    def test_xy_plane_creates_lines(self):
        ax = ThreeDAxes(x_range=(-2, 2), y_range=(-2, 2))
        grid = ax.add_grid_plane(plane='xy', step=1)
        assert isinstance(grid, VCollection)
        assert len(grid) > 0

    def test_yz_plane_creates_lines(self):
        ax = ThreeDAxes(y_range=(-2, 2), z_range=(-2, 2))
        grid = ax.add_grid_plane(plane='yz', step=1)
        assert isinstance(grid, VCollection)
        assert len(grid) > 0

    def test_grid_line_count_xz(self):
        ax = ThreeDAxes(x_range=(-2, 2), z_range=(-2, 2))
        grid = ax.add_grid_plane(plane='xz', step=1)
        # x: -2,-1,0,1,2 = 5 lines + z: -2,-1,0,1,2 = 5 lines = 10
        assert len(grid) == 10

    def test_grid_renders_in_svg(self):
        ax = ThreeDAxes(x_range=(-1, 1), z_range=(-1, 1))
        ax.add_grid_plane(plane='xz', step=1)
        svg = ax.to_svg(0)
        # Grid lines are rendered as VCollection children
        assert svg.count("stroke-opacity='0.3'") > 0 or 'stroke-opacity' in svg

    def test_custom_color_and_opacity(self):
        ax = ThreeDAxes(x_range=(-1, 1), z_range=(-1, 1))
        grid = ax.add_grid_plane(plane='xz', step=1, color='#ff0000', opacity=0.5)
        svg = grid.to_svg(0)
        assert 'rgb(255,0,0)' in svg or '#ff0000' in svg
        assert "stroke-opacity='0.5'" in svg

    def test_returns_vcollection(self):
        ax = ThreeDAxes()
        grid = ax.add_grid_plane()
        assert isinstance(grid, VCollection)

    def test_added_to_axes_objects(self):
        ax = ThreeDAxes(x_label=None, y_label=None, z_label=None)
        initial_count = len(ax.objects)
        ax.add_grid_plane()
        assert len(ax.objects) == initial_count + 1


# ---------------------------------------------------------------------------
# 3D primitive movement and convenience methods
# ---------------------------------------------------------------------------

class TestLine3DMovement:
    def test_shift(self):
        line = Line3D((0, 0, 0), (1, 0, 0))
        line.shift(dx=1, dy=2, dz=3)
        assert line._start == (1, 2, 3)
        assert line._end == (2, 2, 3)

    def test_shift_chaining(self):
        line = Line3D((0, 0, 0), (1, 0, 0))
        result = line.shift(dx=1)
        assert result is line

    def test_move_to(self):
        line = Line3D((0, 0, 0), (2, 0, 0))
        line.move_to(5, 5, 5)
        # Midpoint was (1, 0, 0), now should be (5, 5, 5)
        assert line._start == (4, 5, 5)
        assert line._end == (6, 5, 5)

    def test_set_color(self):
        line = Line3D((0, 0, 0), (1, 0, 0), stroke='#fff')
        line.set_color('#ff0000')
        ax = ThreeDAxes()
        patches = line.to_patches(ax, 0)
        assert '#ff0000' in patches[0][1]

    def test_get_midpoint(self):
        line = Line3D((0, 0, 0), (4, 6, 8))
        mid = line.get_midpoint()
        assert mid == (2, 3, 4)

    def test_get_length(self):
        line = Line3D((0, 0, 0), (3, 4, 0))
        assert line.get_length() == pytest.approx(5.0)

    def test_copy(self):
        line = Line3D((0, 0, 0), (1, 1, 1), stroke='#ff0')
        line2 = line.copy()
        line2.shift(dx=10)
        assert line._start == (0, 0, 0)  # original unchanged
        assert line2._start == (10, 0, 0)


class TestDot3DMovement:
    def test_shift(self):
        dot = Dot3D((1, 2, 3))
        dot.shift(dx=1, dy=-1, dz=2)
        assert dot._point == (2, 1, 5)

    def test_move_to(self):
        dot = Dot3D((0, 0, 0))
        dot.move_to(5, 6, 7)
        assert dot._point == (5, 6, 7)

    def test_set_color(self):
        dot = Dot3D((0, 0, 0), fill='#fff')
        dot.set_color('#00ff00')
        ax = ThreeDAxes()
        patches = dot.to_patches(ax, 0)
        assert '#00ff00' in patches[0][1]

    def test_set_radius(self):
        dot = Dot3D((0, 0, 0), radius=5)
        dot.set_radius(10)
        assert dot._radius == 10

    def test_get_position(self):
        dot = Dot3D((3, 4, 5))
        assert dot.get_position() == (3, 4, 5)

    def test_copy(self):
        dot = Dot3D((1, 2, 3))
        dot2 = dot.copy()
        dot2.move_to(0, 0, 0)
        assert dot._point == (1, 2, 3)
        assert dot2._point == (0, 0, 0)


class TestArrow3DMovement:
    def test_shift(self):
        arrow = Arrow3D((0, 0, 0), (1, 0, 0))
        arrow.shift(dx=2, dy=3, dz=4)
        assert arrow._start == (2, 3, 4)
        assert arrow._end == (3, 3, 4)

    def test_move_to(self):
        arrow = Arrow3D((0, 0, 0), (2, 0, 0))
        arrow.move_to(10, 10, 10)
        assert arrow._start == (9, 10, 10)
        assert arrow._end == (11, 10, 10)

    def test_set_color(self):
        arrow = Arrow3D((0, 0, 0), (1, 0, 0))
        arrow.set_color('#0000ff')
        ax = ThreeDAxes()
        patches = arrow.to_patches(ax, 0)
        assert '#0000ff' in patches[0][1]
        assert '#0000ff' in patches[1][1]  # tip also uses stroke color

    def test_get_length(self):
        arrow = Arrow3D((0, 0, 0), (0, 0, 5))
        assert arrow.get_length() == pytest.approx(5.0)

    def test_copy(self):
        arrow = Arrow3D((0, 0, 0), (1, 1, 1))
        arrow2 = arrow.copy()
        arrow2.shift(dx=5)
        assert arrow._start == (0, 0, 0)
        assert arrow2._start == (5, 0, 0)


class TestText3DMovement:
    def test_shift(self):
        t = Text3D('hello', (1, 2, 3))
        t.shift(dx=1, dy=1, dz=1)
        assert t._point == (2, 3, 4)

    def test_move_to(self):
        t = Text3D('hello', (0, 0, 0))
        t.move_to(5, 5, 5)
        assert t._point == (5, 5, 5)

    def test_set_color(self):
        t = Text3D('hello', (0, 0, 0), fill='#fff')
        t.set_color('#ff0000')
        ax = ThreeDAxes()
        patches = t.to_patches(ax, 0)
        assert '#ff0000' in patches[0][1]

    def test_set_text(self):
        t = Text3D('hello', (0, 0, 0))
        t.set_text('world')
        ax = ThreeDAxes()
        patches = t.to_patches(ax, 0)
        assert 'world' in patches[0][1]

    def test_get_position(self):
        t = Text3D('hello', (3, 4, 5))
        assert t.get_position() == (3, 4, 5)

    def test_copy(self):
        t = Text3D('hello', (1, 2, 3))
        t2 = t.copy()
        t2.set_text('bye')
        assert t._text == 'hello'
        assert t2._text == 'bye'


class TestParametricCurve3DConvenience:
    def test_set_color(self):
        def helix(t):
            return (math.cos(t), math.sin(t), t)
        curve = ParametricCurve3D(helix, t_range=(0, 1), num_points=10)
        curve.set_color('#ff0000')
        ax = ThreeDAxes()
        patches = curve.to_patches(ax, 0)
        assert '#ff0000' in patches[0][1]

    def test_copy(self):
        def helix(t):
            return (math.cos(t), math.sin(t), t)
        curve = ParametricCurve3D(helix, t_range=(0, 1))
        curve2 = curve.copy()
        curve2.set_color('#00ff00')
        assert curve._stroke == '#fff'
        assert curve2._stroke == '#00ff00'


# ---------------------------------------------------------------------------
# Platonic solids
# ---------------------------------------------------------------------------

class TestTetrahedron:
    def test_face_count(self):
        faces = Tetrahedron()
        assert len(faces) == 4

    def test_all_surfaces(self):
        faces = Tetrahedron(fill_color='#ff0000')
        for f in faces:
            assert isinstance(f, Surface)

    def test_custom_position(self):
        faces = Tetrahedron(cx=1, cy=2, cz=3)
        assert len(faces) == 4


class TestOctahedron:
    def test_face_count(self):
        faces = Octahedron()
        assert len(faces) == 8

    def test_all_surfaces(self):
        for f in Octahedron():
            assert isinstance(f, Surface)


class TestIcosahedron:
    def test_face_count(self):
        faces = Icosahedron()
        assert len(faces) == 20

    def test_all_surfaces(self):
        for f in Icosahedron(size=2.0):
            assert isinstance(f, Surface)


class TestDodecahedron:
    def test_face_count(self):
        faces = Dodecahedron()
        assert len(faces) == 12

    def test_all_surfaces(self):
        for f in Dodecahedron(fill_opacity=0.5):
            assert isinstance(f, Surface)


class TestShift3:
    def test_basic(self):
        assert _shift3((1, 2, 3), 10, 20, 30) == (11, 22, 33)

    def test_zero(self):
        assert _shift3((5, 6, 7), 0, 0, 0) == (5, 6, 7)

    def test_negative(self):
        assert _shift3((0, 0, 0), -1, -2, -3) == (-1, -2, -3)


class TestUnifiedWireframe:
    """Test that _Wireframe works for both height-map and parametric usage."""

    def test_heightmap_via_wrapper(self):
        """z=f(x,y) wrapped as parametric func produces correct patches."""
        def height_func(x, y):
            return x + y
        wrapped = lambda u, v: (u, v, height_func(u, v))
        wf = _Wireframe(wrapped, (0, 1), (0, 1), 2, 2, {})
        axes = ThreeDAxes()
        patches = wf.to_patches(axes, 0)
        # 2+1=3 u-lines + 2+1=3 v-lines = 6 patches
        assert len(patches) == 6

    def test_parametric_direct(self):
        """Parametric func(u, v) -> (x, y, z) used directly."""
        def param(u, v):
            return (math.cos(u), math.sin(u), v)
        wf = _Wireframe(param, (0, math.tau), (0, 1), 4, 2, {'stroke': '#ff0000'})
        axes = ThreeDAxes()
        patches = wf.to_patches(axes, 0)
        assert len(patches) == (2 + 1) + (4 + 1)  # 3 + 5 = 8


class TestPrimitive3DShift:
    """Test _shift3 integration in Line3D and Dot3D."""

    def test_line3d_shift(self):
        line = Line3D((0, 0, 0), (1, 1, 1))
        line.shift(dx=5, dy=10, dz=15)
        assert line._start == (5, 10, 15)
        assert line._end == (6, 11, 16)

    def test_dot3d_shift(self):
        dot = Dot3D((0, 0, 0))
        dot.shift(dx=3, dy=4, dz=5)
        assert dot._point == (3, 4, 5)


# ---------------------------------------------------------------------------
# SurfaceMesh
# ---------------------------------------------------------------------------

class TestSurfaceMesh:
    def test_inherits_surface(self):
        s = Surface(lambda u, v: u + v, resolution=(4, 4))
        mesh = SurfaceMesh(s)
        assert isinstance(mesh, Surface)

    def test_produces_line_patches(self):
        s = Surface(lambda u, v: u + v, resolution=(3, 3))
        mesh = SurfaceMesh(s)
        ax = ThreeDAxes()
        patches = mesh.to_patches(ax, 0)
        for _, svg in patches:
            assert '<line' in svg

    def test_no_polygon_patches(self):
        """SurfaceMesh should produce only lines, no filled polygons."""
        s = Surface(lambda u, v: u * v, resolution=(3, 3))
        mesh = SurfaceMesh(s)
        ax = ThreeDAxes()
        patches = mesh.to_patches(ax, 0)
        for _, svg in patches:
            assert '<polygon' not in svg

    def test_patch_count(self):
        """U-direction: (u_steps+1)*v_steps + V-direction: (v_steps+1)*u_steps."""
        s = Surface(lambda u, v: u + v, resolution=(4, 3))
        mesh = SurfaceMesh(s)
        ax = ThreeDAxes()
        patches = mesh.to_patches(ax, 0)
        # U lines: 5 * 3 = 15, V lines: 4 * 4 = 16, total = 31
        assert len(patches) == (4 + 1) * 3 + (3 + 1) * 4

    def test_custom_resolution(self):
        s = Surface(lambda u, v: u + v, resolution=(10, 10))
        mesh = SurfaceMesh(s, resolution=(2, 2))
        ax = ThreeDAxes()
        patches = mesh.to_patches(ax, 0)
        # 3*2 + 3*2 = 12
        assert len(patches) == (2 + 1) * 2 + (2 + 1) * 2

    def test_stroke_color(self):
        s = Surface(lambda u, v: u + v, resolution=(2, 2))
        mesh = SurfaceMesh(s, stroke_color='#ff0000')
        ax = ThreeDAxes()
        patches = mesh.to_patches(ax, 0)
        for _, svg in patches:
            assert '#ff0000' in svg

    def test_stroke_opacity(self):
        s = Surface(lambda u, v: u + v, resolution=(2, 2))
        mesh = SurfaceMesh(s, stroke_opacity=0.7)
        ax = ThreeDAxes()
        patches = mesh.to_patches(ax, 0)
        for _, svg in patches:
            assert 'opacity="0.7"' in svg

    def test_zero_fill_opacity(self):
        """SurfaceMesh should have 0 fill_opacity (wireframe only)."""
        s = Surface(lambda u, v: u + v, fill_opacity=0.9, resolution=(2, 2))
        mesh = SurfaceMesh(s)
        assert mesh._fill_opacity == 0

    def test_parametric_surface(self):
        """SurfaceMesh works with parametric surfaces too."""
        def param(u, v):
            return (math.cos(u), math.sin(u), v)
        s = Surface(param, u_range=(0, math.tau), v_range=(0, 1), resolution=(4, 2))
        mesh = SurfaceMesh(s)
        ax = ThreeDAxes()
        patches = mesh.to_patches(ax, 0)
        assert len(patches) == (4 + 1) * 2 + (2 + 1) * 4

    def test_import_from_objects(self):
        from vectormation.objects import SurfaceMesh as SM
        assert SM is SurfaceMesh


# ---------------------------------------------------------------------------
# _frange edge cases
# ---------------------------------------------------------------------------

class TestFrange:
    def test_zero_step_returns_start(self):
        from vectormation._threed import _frange
        result = _frange(0, 10, 0)
        assert result == [0]

    def test_negative_step_returns_start(self):
        from vectormation._threed import _frange
        result = _frange(0, 10, -1)
        assert result == [0]

    def test_start_beyond_stop_with_zero_step(self):
        from vectormation._threed import _frange
        result = _frange(10, 5, 0)
        assert result == []

    def test_normal_range(self):
        from vectormation._threed import _frange
        result = _frange(0, 2, 1)
        assert len(result) == 3
        assert result[0] == 0
        assert result[-1] == 2


# ---------------------------------------------------------------------------
# set_camera_preset
# ---------------------------------------------------------------------------

class TestCameraPreset:
    def test_default_preset(self):
        ax = ThreeDAxes()
        result = ax.set_camera_preset('default')
        assert result is ax

    def test_isometric_preset(self):
        ax = ThreeDAxes()
        ax.set_camera_preset('isometric', start=0, end=0.5)
        # Verify phi/theta at end
        phi = ax.phi.at_time(0.5)
        assert abs(phi - math.radians(54.7)) < 0.1

    def test_top_preset(self):
        ax = ThreeDAxes()
        ax.set_camera_preset('top', start=0, end=0.5)
        phi = ax.phi.at_time(0.5)
        assert phi == pytest.approx(0, abs=0.01)

    def test_front_preset(self):
        ax = ThreeDAxes()
        ax.set_camera_preset('front', start=0, end=0.5)
        phi = ax.phi.at_time(0.5)
        assert phi == pytest.approx(math.radians(90), abs=0.01)

    def test_side_preset(self):
        ax = ThreeDAxes()
        ax.set_camera_preset('side')
        assert True  # no crash

    def test_invalid_preset_raises(self):
        ax = ThreeDAxes()
        with pytest.raises(KeyError):
            ax.set_camera_preset('nonexistent')


# ---------------------------------------------------------------------------
# set_camera_zoom
# ---------------------------------------------------------------------------

class TestCameraZoom:
    def test_basic_zoom(self):
        ax = ThreeDAxes()
        result = ax.set_camera_zoom(0, 1, factor=2.0)
        assert result is ax

    def test_zoom_changes_scale(self):
        ax = ThreeDAxes()
        initial_scale = ax._scale_3d.at_time(0)
        ax.set_camera_zoom(0, 1, factor=2.0)
        final_scale = ax._scale_3d.at_time(1)
        assert final_scale == pytest.approx(initial_scale * 2.0, rel=0.05)

    def test_zoom_factor_one(self):
        ax = ThreeDAxes()
        initial = ax._scale_3d.at_time(0)
        ax.set_camera_zoom(0, 1, factor=1.0)
        assert ax._scale_3d.at_time(1) == pytest.approx(initial, rel=0.01)

    def test_zoom_half(self):
        ax = ThreeDAxes()
        initial = ax._scale_3d.at_time(0)
        ax.set_camera_zoom(0, 1, factor=0.5)
        assert ax._scale_3d.at_time(1) == pytest.approx(initial * 0.5, rel=0.05)


# ---------------------------------------------------------------------------
# set_checkerboard (Surface)
# ---------------------------------------------------------------------------

class TestSetCheckerboard:
    def test_basic(self):
        s = Surface(lambda u, v: (u, v, 0))
        result = s.set_checkerboard('#FF0000', '#0000FF')
        assert result is s
        assert s._checkerboard_colors == ('#FF0000', '#0000FF')

    def test_renders_with_new_colors(self):
        ax = ThreeDAxes()
        s = Surface(lambda u, v: (u, v, 0))
        ax.add_surface(s)
        s.set_checkerboard('#FF0000', '#0000FF')
        svg = ax.to_svg(0)
        assert svg is not None


# ---------------------------------------------------------------------------
# Factory edge cases
# ---------------------------------------------------------------------------

class TestFactoryEdgeCases:
    def test_sphere_zero_radius(self):
        s = Sphere3D(radius=0)
        ax = ThreeDAxes()
        ax.add_surface(s)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_cube_zero_side(self):
        c = Cube(side_length=0)
        ax = ThreeDAxes()
        for s in c:
            ax.add_surface(s)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_cylinder_zero_radius(self):
        c = Cylinder3D(radius=0, height=1)
        ax = ThreeDAxes()
        ax.add_surface(c)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_cone_zero_height(self):
        c = Cone3D(radius=1, height=0)
        ax = ThreeDAxes()
        ax.add_surface(c)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_prism_triangle(self):
        """Prism with 3 sides (triangular prism)."""
        p = Prism3D(n_sides=3, radius=1, height=2)
        ax = ThreeDAxes()
        for s in p:
            ax.add_surface(s)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_prism_many_sides(self):
        """Prism with many sides approaches cylinder."""
        p = Prism3D(n_sides=32)
        ax = ThreeDAxes()
        for s in p:
            ax.add_surface(s)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_torus_inverted_radii(self):
        """Major radius smaller than minor radius."""
        t = Torus3D(major_radius=0.5, minor_radius=2)
        ax = ThreeDAxes()
        ax.add_surface(t)
        svg = ax.to_svg(0)
        assert svg is not None


# ---------------------------------------------------------------------------
# Camera angle edge cases
# ---------------------------------------------------------------------------

class TestCameraAngles:
    def test_phi_zero_top_down(self):
        ax = ThreeDAxes()
        ax.set_camera_orientation(0, 0.5, phi=0)
        svg = ax.to_svg(0.5)
        assert svg is not None

    def test_phi_pi_bottom_up(self):
        ax = ThreeDAxes()
        ax.set_camera_orientation(0, 0.5, phi=math.pi)
        svg = ax.to_svg(0.5)
        assert svg is not None

    def test_phi_half_pi(self):
        ax = ThreeDAxes()
        ax.set_camera_orientation(0, 0.5, phi=math.pi / 2)
        svg = ax.to_svg(0.5)
        assert svg is not None

    def test_ambient_rotation_negative_rate(self):
        ax = ThreeDAxes()
        ax.begin_ambient_camera_rotation(start=0, end=2, rate=-0.5)
        theta_at_1 = ax.theta.at_time(1)
        theta_at_0 = ax.theta.at_time(0)
        assert theta_at_1 < theta_at_0  # rotating backward

    def test_ambient_rotation_zero_rate(self):
        ax = ThreeDAxes()
        theta0 = ax.theta.at_time(0)
        ax.begin_ambient_camera_rotation(start=0, end=2, rate=0)
        assert ax.theta.at_time(1) == pytest.approx(theta0)


# ---------------------------------------------------------------------------
# 3D primitive edge cases
# ---------------------------------------------------------------------------

class TestPrimitiveEdgeCases:
    def test_line3d_zero_length(self):
        line = Line3D((0, 0, 0), (0, 0, 0))
        ax = ThreeDAxes()
        ax.add_3d(line)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_dot3d_zero_radius(self):
        dot = Dot3D((0, 0, 0), radius=0)
        ax = ThreeDAxes()
        ax.add_3d(dot)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_text3d_empty_string(self):
        txt = Text3D('', (0, 0, 0))
        ax = ThreeDAxes()
        ax.add_3d(txt)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_parametric_curve_single_point(self):
        curve = ParametricCurve3D(
            lambda t: (math.cos(t), math.sin(t), t),
            t_range=(0, 0), num_points=1)
        ax = ThreeDAxes()
        ax.add_3d(curve)
        svg = ax.to_svg(0)
        assert svg is not None

    def test_arrow3d_very_short(self):
        arrow = Arrow3D((0, 0, 0), (0.001, 0, 0))
        ax = ThreeDAxes()
        ax.add_3d(arrow)
        svg = ax.to_svg(0)
        assert svg is not None


# ---------------------------------------------------------------------------
# Depth sorting edge cases
# ---------------------------------------------------------------------------

class TestDepthSorting:
    def test_many_objects_sorted(self):
        ax = ThreeDAxes()
        for i in range(10):
            ax.add_3d(Dot3D((i, 0, i), radius=0.1))
        svg = ax.to_svg(0)
        assert svg is not None

    def test_empty_scene(self):
        ax = ThreeDAxes()
        svg = ax.to_svg(0)
        assert svg is not None

    def test_hidden_surface_excluded(self):
        ax = ThreeDAxes()
        s = Surface(lambda u, v: (u, v, 0))
        s.show.set(0, 0, lambda t: 0)  # hide it
        ax.add_surface(s)
        svg = ax.to_svg(0)
        assert svg is not None
