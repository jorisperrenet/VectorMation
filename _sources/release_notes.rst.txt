Release Notes
=============

v2.5
----

3D Overhaul
^^^^^^^^^^^

- **ThreeDAxes** rewritten in new ``_threed.py`` module — replaces the old isometric projection with proper orthographic projection, animatable camera angles (``phi``/``theta``), depth-sorted rendering, Lambertian shading, and LaTeX axis labels
- **Surface**: Filled quad surfaces with checkerboard colours and Lambertian shading
- **3D primitives**: ``Line3D``, ``Dot3D``, ``Arrow3D``, ``ParametricCurve3D``, ``Text3D``
- **3D factories**: ``Sphere3D``, ``Cube``, ``Cylinder3D``, ``Cone3D``, ``Torus3D``, ``Prism3D``
- ``set_camera_orientation()``, ``begin_ambient_camera_rotation()``, ``set_light_direction()`` for camera and lighting control
- Old isometric ``ThreeDAxes`` removed from ``_composites.py``

Axes Improvements
^^^^^^^^^^^^^^^^^

- ``Axes.add_function()`` / ``plot()`` now accepts ``x_range=(min, max)`` to limit the curve domain, with ``lincl``/``rincl`` for inclusive/exclusive bounds
- Domain boundaries stored as animatable ``Real`` attributes (``._domain_min``, ``._domain_max``)
- ``Axes`` gains ``equal_aspect`` parameter — adjusts ``plot_height`` to match the x/y aspect ratio
- ``_sample_function()`` accepts ``extra_xs`` for injecting exact sample points at domain boundaries

Camera Improvements
^^^^^^^^^^^^^^^^^^^

- ``camera_zoom()`` now centres the viewBox on the target point and clamps to canvas bounds
- ``camera_follow()`` clamps the viewBox to stay within canvas bounds (no negative offsets)
- ``_resolve_end_time()`` now considers camera viewBox attributes (``vb_x``, ``vb_y``, ``vb_w``, ``vb_h``), so camera-only animations are included in auto-detected end times

Bug Fixes
^^^^^^^^^

- **ZoomedInset fadein/fadeout**: ``ZoomedInset.to_svg()`` now wraps its output in a ``<g>`` with ``self.styling.svg_style(time)`` applied, so ``fadein()``, ``fadeout()``, and other styling animations (opacity, transforms) take effect

Documentation
^^^^^^^^^^^^^

- **vs Manim page**: All 26 Manim examples now covered (was 22) — added SineCurveUnitCircle, GradientImageFromArray, ThreeDCameraRotation, ParametricCurve3DExample, FollowingGraphCamera; removed "Not Applicable" section
- 3D section updated: descriptions reflect filled surfaces, Lambertian shading, and camera rotation instead of wireframes
- **Reference pages**: Added parameter diagrams for shapes (Ellipse, Circle, Rectangle, Line, RegularPolygon, Star, Arc, Wedge, Annulus, Angle), composites (Arrow, CurvedArrow, Brace, NumberLine), graphing (Axes anatomy), collections (arrange), and VObject (coordinate system, edges, next\_to)
- **Attributes page**: Added easing curves diagram
- **Examples page**: Added EasingPreview, GraphExample, CodeExplanation, and Logo examples
- **three_d_camera example**: Added missing ``export_video`` call so the Makefile can generate the mp4 asset
- **Makefile**: Added new video/SVG targets (following\_graph\_camera, sine\_curve\_unit\_circle, three\_d\_camera, gradient\_image, three\_d\_helix)

----

v2.4
----

New Shapes and Classes
^^^^^^^^^^^^^^^^^^^^^^

- **ThreeDAxes**: Isometric 3D axes with ``plot_parametric_surface(func, u_range, v_range)`` for wireframe surfaces
- **ZoomedInset**: Magnify a region of the canvas into a separate display area with animated source movement
- **Boolean operations**: ``Union``, ``Difference``, ``Exclusion``, ``Intersection`` — combine two shapes with correct fill and boundary strokes using SVG clip-paths
- **Table**: Grid of text/objects with row and column labels
- **Matrix**: Table styled as a mathematical matrix with brackets
- **DynamicObject**: Object that re-evaluates a callable each frame
- **ValueTracker**: Invisible animatable value for driving updaters
- **DecimalNumber**: Text that displays and animates a numeric value
- **Title**: Centered title text with underline
- **ScreenRectangle**: Rectangle matching the canvas aspect ratio
- **SurroundingRectangle** / **BackgroundRectangle**: Rectangles that fit around other objects
- **always_redraw(func)**: Convenience wrapper for ``DynamicObject``

Axes Improvements
^^^^^^^^^^^^^^^^^

- ``Axes.add_function(func, label, label_direction, label_x_val, stroke)`` — plot a function and optionally label it in one call (``plot`` is an alias)
- ``y_range`` is now optional in ``Axes`` — when omitted, the y-axis range is auto-determined from the first plotted function
- ``Graph`` inherits ``add_function`` from ``Axes``

Boolean Operations Fix
^^^^^^^^^^^^^^^^^^^^^^

- ``shift()``, ``move_to()``, ``center_to_pos()``, ``scale()`` now work on boolean operation objects
- Each operation renders with correct SVG clip-paths:

  - **Intersection**: clips each shape to the other; strokes trace only the intersection boundary
  - **Union**: fill via nonzero fill-rule; strokes use inverse clips to hide interior boundaries
  - **Difference**: evenodd fill clipped to shape A; strokes show A outside B and B inside A
  - **Exclusion**: single evenodd path (unchanged)

- Styling transforms (scale, rotate) are applied on a wrapping ``<g>`` so clip regions transform correctly

New Exports
^^^^^^^^^^^

- Direction and size constants are now public: ``UP``, ``DOWN``, ``LEFT``, ``RIGHT``, ``UL``, ``UR``, ``DL``, ``DR``, ``ORIGIN``, ``UNIT``, ``SMALL_BUFF``, ``MED_SMALL_BUFF``, ``MED_LARGE_BUFF``, ``LARGE_BUFF``, and default size constants
- ``VGroup`` alias for ``VCollection``

Internal Improvements
^^^^^^^^^^^^^^^^^^^^^

- ``objects.py`` split into sub-modules: ``_base.py``, ``_shapes.py``, ``_composites.py``, ``_canvas.py``, ``_constants.py`` (public API unchanged)

Documentation
^^^^^^^^^^^^^

- **3D examples**: three_d_axes, three_d_surface_plot, three_d_sphere added to vs Manim page
- **Boolean operations** and **zoomed inset** video examples added to Makefile
- Cleaned up orphaned Makefile targets

Test Suite
^^^^^^^^^^

- 697 tests

----

v2.3
----

New Shapes and Classes
^^^^^^^^^^^^^^^^^^^^^^

- **Axes**: Standalone axes with tick labels, axis labels, and ``plot()`` method
- **NumberPlane**: Coordinate grid with major/minor gridlines, axis labels, and background lines
- **Angle**: Arc with label between two lines, tracks angle dynamically via updaters

Visual Defaults (Manim Parity)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Default ``stroke_width``: 4 -> 5 (matches Manim's cairo rendering)
- Arrow tip: ``tip_length`` 18 -> 47, ``tip_width`` 12 -> 47
- Axis/number-line stroke: 4 -> 3 (matches Manim's NumberLine default)
- Tick stroke: 2 -> 3
- Tick label font size: 48 -> 24

Export
^^^^^^

- **SVG frame export**: ``canvas.write_frame(time, filename)`` writes a single frame as native SVG (no cairosvg dependency)

Bug Fixes
^^^^^^^^^

- **XML escaping**: ``Text.to_svg()`` now escapes ``&``, ``<``, ``>`` in text content

Internal Improvements
^^^^^^^^^^^^^^^^^^^^^

- Per-frame logging moved to level 5 (below DEBUG) so it doesn't appear in verbose mode
- LaTeX cache-hit logging also moved to level 5

Documentation
^^^^^^^^^^^^^

- Full Sphinx documentation with Furo theme
- **Makefile** for docs: dependency-tracked, parallel builds (``make html``, ``make assets``, ``make serve``)
- **Examples page**: all examples include video or SVG previews
- **vs Manim page**: side-by-side comparison with Manim Community examples
- **Tutorial**: step-by-step first animation guide
- **Reference manual**: objects, animation, attributes, graphing, and styling

Test Suite
^^^^^^^^^^

- 565 tests

----

v2.2
----

Default Argument Changes
^^^^^^^^^^^^^^^^^^^^^^^^

- ``Tup.interpolate`` easing: ``smooth`` → ``linear`` (matches ``Real`` and ``Color``)
- ``fadein()``, ``fadeout()``, ``write()`` easing: ``linear`` → ``smooth`` (natural fade-in/out)
- ``VCollection.write`` max\_stroke\_width: ``0.5`` → ``1`` (matches ``VObject.write``)
- ``brect()`` parameter renamed ``dpos`` → ``buff``, default ``5`` → ``10``
- ``arrange()`` buff: ``20`` → ``10`` (tighter default layout)
- ``CurvedArrow`` tip: ``tip_length=12, tip_width=8`` → ``tip_length=15, tip_width=10`` (matches ``Arrow``)
- ``Ellipse`` default styling: removed hardcoded ``fill='#e07a5f'``; now uses ``stroke='#fff', stroke_width=2``

Bug Fixes
^^^^^^^^^

- **always\_rotate**: fixed absolute-time bug where ``deg = degrees_per_second * t`` used the global clock instead of relative time ``(t - start)``, causing an instant rotation jump at the start

Browser Viewer
^^^^^^^^^^^^^^

- **Frame stepping**: press ``,`` / ``.`` (or ``<`` / ``>``) to step one frame backward / forward
- **Help overlay**: press ``?`` or click the ``?`` button (right side of toolbar) to view all keyboard shortcuts

Packaging
^^^^^^^^^

- Added ``pyproject.toml`` with full project metadata, dependencies, and optional ``[export]`` extras
- Fixed installation docs: numpy purpose corrected to "Path morphing interpolation"

Removed
^^^^^^^

- ``FixedVertexPolygon`` backward-compat alias (use ``Polygon`` directly)

Other
^^^^^

- Updated copyright to 2023-2025

Test Suite
^^^^^^^^^^

- 507 tests

----

v2.1
----

New Shapes and Classes
^^^^^^^^^^^^^^^^^^^^^^

- **FunctionGraph**: Plot a function as a bare polyline (no axes/ticks/labels)
- **Star**: N-pointed star polygon with configurable inner/outer radius
- **Annulus**: Ring/donut shape with inner and outer radius
- **DashedLine**: Line with configurable dash pattern
- **RoundedRectangle**: Rectangle with rounded corners
- **DoubleArrow**: Shorthand for ``Arrow(double_ended=True)``
- **CurvedArrow**: Arrow with a quadratic bezier shaft
- **CountAnimation**: Text that animates a number counting between values
- **NumberLine**: Number line with ticks, labels, and ``number_to_point()`` mapping
- **Trace**: Follow a coordinate attribute over time, drawing a polyline trail

New Methods
^^^^^^^^^^^

- ``VObject.__repr__()`` / ``VCollection.__repr__()`` for readable debug output
- ``VObject.become(other, time)`` now copies all style attributes (not just a subset)
- ``VObject.indicate()``, ``flash()``, ``pulse()``, ``wiggle()``, ``circumscribe()`` -- visual effect animations
- ``VObject.along_path()`` -- move centre along an SVG path
- ``VObject.always_rotate()`` -- updater-based continuous rotation
- ``VObject.match_width()`` / ``match_height()`` -- scale to match another object
- ``VCollection.arrange()`` -- lay out children in a row or column
- ``VCollection.stagger()`` -- call a method on each child with staggered timing

Export
^^^^^^

- **PNG export**: ``canvas.export_png(time, filename, width, height)`` via cairosvg
- **Video export**: ``canvas.export_video(filename, start_time, end_time, fps)`` via cairosvg + ffmpeg
- **GIF export**: ``canvas.export_gif(filename, start_time, end_time, fps, scale, loop)`` via cairosvg + Pillow

Browser Viewer
^^^^^^^^^^^^^^

- **Debug panel** (press **D**): shows current time, frame number, and visible objects
- **Snap mode** (press **N**): cursor snaps to nearby object points
- **Arrow keys**: Right arrow jumps to next section, Left arrow steps backward

Internal Improvements
^^^^^^^^^^^^^^^^^^^^^

- ``scale()`` delegates to ``stretch()`` (less code duplication)
- ``_transform_points()`` reads styling attrs directly (avoids string re-parsing)
- Shared ``_sample_function()`` helper for Graph and FunctionGraph (DRY)
- ``become()`` uses ``style._STYLES`` for all attrs instead of hardcoded subset
- ``Styling.interpolate`` uses module-level ``_ATTR_NAMES`` constant
- ``_SVG_SHAPE_TAGS`` is a frozenset

Test Suite
^^^^^^^^^^

- Tests covering attributes, morphing, path bbox, objects, shapes, styling, and canvas

----

v2.0
----

New Features
^^^^^^^^^^^^

- **Browser-based viewer**: WebSocket-powered browser display with zoom, pan, keyboard controls, hot reload, and a debug panel (press 'D')
- **Draw-along animation**: ``VObject.draw_along(start, end, easing)`` animates stroke drawing via stroke-dashoffset
- **Scale/rotate helpers**: ``scale_to()``, ``rotate_to()``, ``scale_by()``, ``rotate_by()`` on both VObject and VCollection
- **Staggered animations**: ``VCollection.stagger(method_name, delay, **kwargs)`` offsets timing for each sub-object
- **HSL color interpolation**: ``Color.interpolate_hsl()`` and ``color_space='hsl'`` parameter on ``Color.interpolate()``
- **Path following**: ``Coor.along_path(start, end, path_d)`` moves a coordinate along an SVG path by arc length
- **GIF export**: ``VectorMathAnim.export_gif()`` using cairosvg and Pillow
- **Brace annotation**: ``Brace(target, direction, label, buff)`` curly brace shape
- **VObject.copy()**: Deep copy with independent animations
- **VCollection indexing**: ``collection[i]``, ``len(collection)`` support
- **from_svg_file()**: Load an SVG file into a VCollection of parseable elements
- **Graph class**: Plot mathematical functions with axes, ticks, labels, and grid
- **Arrow class**: Line with triangular arrowhead, optional double-ended
- **Arc / Wedge**: SVG arc and pie-wedge shapes with animatable parameters
- **ClipPath**: SVG clip path definitions
- **RegularPolygon**: N-sided regular polygon inscribed in a circle

New Shapes and Classes
^^^^^^^^^^^^^^^^^^^^^^

- ``Graph``, ``Arrow``, ``Brace``, ``Arc``, ``Wedge``, ``ClipPath``, ``RegularPolygon``, ``SplitTexObject``

Improvements
^^^^^^^^^^^^

- Gradient color support (LinearGradient/RadialGradient work as fill/stroke values)
- Float precision fix in attribute ``set_at()`` (uses epsilon tolerance)
- Fixed color default comparison in ``Styling.svg_style()`` (pre-renders Color defaults)
- Better LaTeX error reporting (parses log file for error messages)
- Arc morphing now works (Arc.to_bezier approximates via cubic curves)
- Zoom-out clamped at 4x canvas dimensions in browser viewer
- Debug panel in browser viewer (toggle with 'D' key)
- Added ``lxml`` to requirements for faster XML parsing

Removed
^^^^^^^

- ``window.py`` and ``utils.py`` (dead PyQt5 viewer code)
- ``standard_display()`` replaced by ``browser_display()``

Test Suite
^^^^^^^^^^

- 218+ tests covering attributes, shapes, styling, canvas, easings, collections, and colors
- Run with ``pytest tests/ -v``
