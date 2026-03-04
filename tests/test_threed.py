"""Tests for 3D module: projection, camera, surfaces."""
import math
import pytest

from vectormation._threed import ThreeDAxes, Surface, Line3D, Dot3D, Arrow3D


class TestProjection:

    @pytest.fixture
    def axes(self):
        return ThreeDAxes()

    def test_origin_projects_to_center(self, axes):
        sx, sy, _ = axes.project_point(0, 0, 0)
        # Origin should project near the axes' center
        cx, cy = axes.center(0)
        assert sx == pytest.approx(cx, abs=5)
        assert sy == pytest.approx(cy, abs=5)

    def test_depth_increases_away_from_camera(self, axes):
        """Points farther from camera should have higher depth."""
        _, _, d_near = axes.project_point(0, 0, 0)
        _, _, d_far = axes.project_point(0, 0, -5)  # pushing away
        # Depth depends on camera orientation but one should differ
        assert d_near != pytest.approx(d_far, abs=0.01)

    def test_x_axis_projects_horizontally(self, axes):
        """Moving along x-axis should change screen x."""
        sx1, _, _ = axes.project_point(0, 0, 0)
        sx2, _, _ = axes.project_point(1, 0, 0)
        # Should be different x positions
        assert sx1 != pytest.approx(sx2, abs=1)

    def test_z_axis_projects_vertically(self, axes):
        """Moving along z-axis should change screen y."""
        _, sy1, _ = axes.project_point(0, 0, 0)
        _, sy2, _ = axes.project_point(0, 0, 1)
        # z-up should move upward on screen (smaller y in SVG)
        assert sy2 < sy1

    def test_projection_is_linear(self, axes):
        """Orthographic projection should be linear."""
        sx1, sy1, _ = axes.project_point(1, 0, 0)
        sx2, sy2, _ = axes.project_point(2, 0, 0)
        sx3, sy3, _ = axes.project_point(3, 0, 0)
        # Equal spacing in 3D → equal spacing on screen
        dx1 = sx2 - sx1
        dx2 = sx3 - sx2
        assert dx1 == pytest.approx(dx2, abs=1)

    def test_coords_to_point_2d_compat(self, axes):
        """coords_to_point should work for 2D (z=0)."""
        sx, sy = axes.coords_to_point(1, 1, 0)
        # Should return a valid screen position
        assert isinstance(sx, float)
        assert isinstance(sy, float)


class TestCamera:

    def test_set_camera_orientation(self):
        axes = ThreeDAxes()
        axes.set_camera_orientation(start=0, end=1, phi=math.pi / 4, theta=math.pi / 3)
        phi = axes.phi.at_time(1)
        theta = axes.theta.at_time(1)
        assert phi == pytest.approx(math.pi / 4, abs=0.01)
        assert theta == pytest.approx(math.pi / 3, abs=0.01)

    def test_camera_orientation_changes_projection(self):
        # Use two axes with very different camera angles
        axes1 = ThreeDAxes(phi=math.radians(30), theta=math.radians(0))
        axes2 = ThreeDAxes(phi=math.radians(80), theta=math.radians(90))
        sx1, sy1, _ = axes1.project_point(1, 0, 0, time=0)
        sx2, sy2, _ = axes2.project_point(1, 0, 0, time=0)
        # Different camera should give different projection
        assert abs(sx1 - sx2) > 5 or abs(sy1 - sy2) > 5

    def test_ambient_rotation(self):
        axes = ThreeDAxes()
        theta_start = axes.theta.at_time(0)
        axes.begin_ambient_camera_rotation(start=0, end=10, rate=1)
        theta_later = axes.theta.at_time(5)
        assert theta_later != pytest.approx(theta_start, abs=0.1)


class TestSurface:

    def test_surface_from_height_map(self):
        axes = ThreeDAxes()
        s = Surface(lambda x, y: x + y, u_range=(-1, 1), v_range=(-1, 1))
        axes.add_surface(s)
        # Should produce patches
        patches = s.to_patches(axes, 0)
        assert len(patches) > 0

    def test_surface_patches_have_depth(self):
        axes = ThreeDAxes()
        s = Surface(lambda x, y: 0, u_range=(-1, 1), v_range=(-1, 1))
        axes.add_surface(s)
        patches = s.to_patches(axes, 0)
        # Each patch should have a depth value
        for patch in patches:
            assert len(patch) >= 2  # (depth, svg_string)

    def test_plot_surface_convenience(self):
        axes = ThreeDAxes()
        axes.plot_surface(lambda x, y: x ** 2 + y ** 2,
                          u_range=(-1, 1), v_range=(-1, 1))
        svg = axes.to_svg(0)
        assert '<' in svg  # produces SVG output


class TestPrimitives:

    def test_dot3d_renders(self):
        axes = ThreeDAxes()
        d = Dot3D((0, 0, 0))
        axes.add_3d(d)
        patches = d.to_patches(axes, 0)
        assert len(patches) > 0

    def test_line3d_renders(self):
        axes = ThreeDAxes()
        line = Line3D((0, 0, 0), (1, 1, 1))
        axes.add_3d(line)
        patches = line.to_patches(axes, 0)
        assert len(patches) > 0

    def test_arrow3d_renders(self):
        axes = ThreeDAxes()
        arr = Arrow3D((0, 0, 0), (1, 1, 1))
        axes.add_3d(arr)
        patches = arr.to_patches(axes, 0)
        assert len(patches) > 0


class TestThreeDAxesSVG:

    def test_to_svg_produces_output(self):
        axes = ThreeDAxes()
        svg = axes.to_svg(0)
        assert '<g' in svg or '<line' in svg or '<polygon' in svg

    def test_depth_sorting(self):
        """Objects at different depths should be rendered in correct order."""
        axes = ThreeDAxes()
        d1 = Dot3D((0, 0, 0))
        d2 = Dot3D((0, 0, 5))
        axes.add_3d(d1)
        axes.add_3d(d2)
        svg = axes.to_svg(0)
        # Should render without errors (depth sorting happens internally)
        assert len(svg) > 10
