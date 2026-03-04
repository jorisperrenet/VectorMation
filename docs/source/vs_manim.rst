vs Manim
========

This page compares VectorMation with `Manim Community <https://www.manim.community/>`_ side by side. Each example is taken from the `Manim examples gallery <https://docs.manim.community/en/stable/examples.html>`_. All VectorMation examples are runnable from ``examples/manim/``.

Key Differences
---------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * -
     - VectorMation
     - Manim
   * - **Output**
     - Native SVG
     - Rasterized video (Cairo/OpenGL)
   * - **Approach**
     - Declarative: define animations, view any frame
     - Imperative: ``self.play()`` each step
   * - **Structure**
     - Plain script
     - Class with ``construct()`` method
   * - **Preview**
     - Hot-reload browser viewer
     - Re-render on every change
   * - **Angles**
     - Degrees
     - Radians (``PI / 4``)
   * - **Timing**
     - Seconds as floats (``start=1, end=3``)
     - ``run_time`` per ``self.play()`` call
   * - **Coordinates**
     - Pixel-based (1920x1080 viewBox, center at 960, 540)
     - Unit-based (centered at ORIGIN)

Philosophy
----------

**Manim** treats animation as a sequence of actions: create a shape, play an animation, wait, play another. Every step is explicitly played through ``self.play()``.

**VectorMation** treats objects as **functions of time**: you define *what* should happen and *when*, and the library renders any frame on demand. This means no ``self.play()`` calls, no ``self.wait()``, and instant hot-reload in the browser.

----

Basic Concepts
--------------

.. admonition:: Example: ManimCELogo
   :class: example

   .. raw:: html

      <img src="_static/videos/manim_community_logo.svg">

   Logo recreation with basic shapes.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/manim_community_logo.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class ManimCELogo(Scene):
                def construct(self):
                    self.camera.background_color = "#ece6e2"
                    ds_m = MathTex(r"\mathbb{M}", fill_color="#343434").scale(7)
                    ds_m.shift(2.25 * LEFT + 1.5 * UP)
                    circle = Circle(color="#87c2a5", fill_opacity=1).shift(LEFT)
                    square = Square(color="#525893", fill_opacity=1).shift(UP)
                    triangle = Triangle(color="#e07a5f", fill_opacity=1).shift(RIGHT)
                    logo = VGroup(triangle, square, circle, ds_m)
                    logo.move_to(ORIGIN)
                    self.add(logo)

.. admonition:: Example: BraceAnnotation
   :class: example

   .. raw:: html

      <img src="_static/videos/brace_annotation.svg">

   A line with curly brace annotations.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/brace_annotation.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class BraceAnnotation(Scene):
                def construct(self):
                    dot = Dot([-2, -1, 0])
                    dot2 = Dot([2, 1, 0])
                    line = Line(dot.get_center(), dot2.get_center()).set_color(ORANGE)
                    b1 = Brace(line)
                    b1text = b1.get_text("Horizontal distance")
                    b2 = Brace(line, direction=line.copy().rotate(PI / 2).get_unit_vector())
                    b2text = b2.get_tex("x-x_1")
                    self.add(line, dot, dot2, b1, b2, b1text, b2text)

.. admonition:: Example: VectorArrow
   :class: example

   .. raw:: html

      <img src="_static/videos/vector_arrow.svg">

   An arrow on a number plane with labels.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/vector_arrow.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class VectorArrow(Scene):
                def construct(self):
                    dot = Dot(ORIGIN)
                    arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
                    numberplane = NumberPlane()
                    origin_text = Text('(0, 0)').next_to(dot, DOWN)
                    tip_text = Text('(2, 2)').next_to(arrow.get_end(), RIGHT)
                    self.add(numberplane, dot, arrow, origin_text, tip_text)

----

Animations
----------

.. admonition:: Example: PointMovingOnShapes
   :class: example

   .. raw:: html

      <video src="_static/videos/point_moving_on_shapes.mp4" controls autoplay loop muted></video>

   A dot moves along a circle and then rotates around a point.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/point_moving_on_shapes.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class PointMovingOnShapes(Scene):
                def construct(self):
                    circle = Circle(radius=1, color=BLUE)
                    dot = Dot()
                    dot2 = dot.copy().shift(RIGHT)
                    self.add(dot)
                    line = Line([3, 0, 0], [5, 0, 0])
                    self.add(line)
                    self.play(GrowFromCenter(circle))
                    self.play(Transform(dot, dot2))
                    self.play(MoveAlongPath(dot, circle), run_time=2, rate_func=linear)
                    self.play(Rotating(dot, about_point=[2, 0, 0]), run_time=1.5)

.. admonition:: Example: MovingAround
   :class: example

   .. raw:: html

      <video src="_static/videos/moving_around.mp4" controls autoplay loop muted></video>

   A square shifts, changes colour, scales, and rotates.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/moving_around.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class MovingAround(Scene):
                def construct(self):
                    square = Square(color=BLUE, fill_opacity=1)
                    self.play(square.animate.shift(LEFT))
                    self.play(square.animate.set_fill(ORANGE))
                    self.play(square.animate.scale(0.3))
                    self.play(square.animate.rotate(0.4))

.. admonition:: Example: MovingAngle
   :class: example

   .. raw:: html

      <video src="_static/videos/moving_angle.mp4" controls autoplay loop muted></video>

   An angle indicator tracks a rotating line.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/moving_angle.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class MovingAngle(Scene):
                def construct(self):
                    rotation_center = LEFT
                    theta_tracker = ValueTracker(110)
                    line1 = Line(LEFT, RIGHT)
                    line_moving = Line(LEFT, RIGHT)
                    line_ref = line_moving.copy()
                    line_moving.rotate(
                        theta_tracker.get_value() * DEGREES, about_point=rotation_center
                    )
                    a = Angle(line1, line_moving, radius=0.5, other_angle=False)
                    tex = MathTex(r"\theta").move_to(
                        Angle(line1, line_moving, radius=0.5 + 3 * SMALL_BUFF,
                              other_angle=False).point_from_proportion(0.5)
                    )
                    self.add(line1, line_moving, a, tex)
                    line_moving.add_updater(
                        lambda x: x.become(line_ref.copy()).rotate(
                            theta_tracker.get_value() * DEGREES, about_point=rotation_center
                        )
                    )
                    a.add_updater(
                        lambda x: x.become(Angle(line1, line_moving, radius=0.5))
                    )
                    self.play(theta_tracker.animate.set_value(40))
                    self.play(theta_tracker.animate.increment_value(140))
                    self.play(theta_tracker.animate.set_value(350))

.. admonition:: Example: MovingDots
   :class: example

   .. raw:: html

      <video src="_static/videos/moving_dots.mp4" controls autoplay loop muted></video>

   Two dots move independently with a line tracking between them.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/moving_dots.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class MovingDots(Scene):
                def construct(self):
                    d1, d2 = Dot(color=BLUE), Dot(color=GREEN)
                    dg = VGroup(d1, d2).arrange(RIGHT, buff=1)
                    l1 = Line(d1.get_center(), d2.get_center()).set_color(RED)
                    x = ValueTracker(0)
                    y = ValueTracker(0)
                    d1.add_updater(lambda z: z.set_x(x.get_value()))
                    d2.add_updater(lambda z: z.set_y(y.get_value()))
                    l1.add_updater(lambda z: z.become(Line(d1.get_center(), d2.get_center())))
                    self.add(d1, d2, l1)
                    self.play(x.animate.set_value(5))
                    self.play(y.animate.set_value(4))

.. admonition:: Example: MovingGroupToDestination
   :class: example

   .. raw:: html

      <video src="_static/videos/moving_group.mp4" controls autoplay loop muted></video>

   A group of dots shifts so that the red dot lands on the yellow dot.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/moving_group.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class MovingGroupToDestination(Scene):
                def construct(self):
                    group = VGroup(Dot(LEFT), Dot(ORIGIN), Dot(RIGHT, color=RED), Dot(2 * RIGHT)).scale(1.4)
                    dest = Dot([4, 3, 0], color=YELLOW)
                    self.add(group, dest)
                    self.play(group.animate.shift(dest.get_center() - group[2].get_center()))

.. admonition:: Example: MovingFrameBox
   :class: example

   .. raw:: html

      <video src="_static/videos/moving_frame_box.mp4" controls autoplay loop muted></video>

   A surrounding rectangle highlights parts of an equation.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/moving_frame_box.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class MovingFrameBox(Scene):
                def construct(self):
                    text = MathTex(
                        r"\frac{d}{dx}f(x)g(x)=", r"f(x)\frac{d}{dx}g(x)", "+",
                        r"g(x)\frac{d}{dx}f(x)"
                    )
                    self.play(Write(text))
                    framebox1 = SurroundingRectangle(text[1], buff=.1)
                    framebox2 = SurroundingRectangle(text[3], buff=.1)
                    self.play(Create(framebox1))
                    self.play(ReplacementTransform(framebox1, framebox2))

.. admonition:: Example: RotationUpdater
   :class: example

   .. raw:: html

      <video src="_static/videos/rotation_updater.mp4" controls autoplay loop muted></video>

   A line rotates forward, then reverses direction.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/rotation_updater.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class RotationUpdater(Scene):
                def construct(self):
                    def updater_forth(mobj, dt):
                        mobj.rotate_about_origin(dt)
                    def updater_back(mobj, dt):
                        mobj.rotate_about_origin(-dt)
                    line_reference = Line(ORIGIN, LEFT).set_color(WHITE)
                    line_moving = Line(ORIGIN, LEFT).set_color(YELLOW)
                    line_moving.add_updater(updater_forth)
                    self.add(line_reference, line_moving)
                    self.wait(2)
                    line_moving.remove_updater(updater_forth)
                    line_moving.add_updater(updater_back)
                    self.wait(2)

.. admonition:: Example: PointWithTrace
   :class: example

   .. raw:: html

      <video src="_static/videos/point_with_trace.mp4" controls autoplay loop muted></video>

   A dot moves along a path leaving a visible trace behind it.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/point_with_trace.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class PointWithTrace(Scene):
                def construct(self):
                    path = VMobject()
                    dot = Dot()
                    path.set_points_as_corners([dot.get_center(), dot.get_center()])
                    def update_path(path):
                        previous_path = path.copy()
                        previous_path.add_points_as_corners([dot.get_center()])
                        path.become(previous_path)
                    path.add_updater(update_path)
                    self.add(path, dot)
                    self.play(Rotating(dot, angle=PI, about_point=RIGHT, run_time=2))
                    self.play(dot.animate.shift(UP))
                    self.play(dot.animate.shift(LEFT))

.. admonition:: Example: SineCurveUnitCircle
   :class: example

   .. raw:: html

      <video src="_static/videos/sine_curve_unit_circle.mp4" controls autoplay loop muted></video>

   A dot moves around a unit circle, tracing out a sine curve.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/sine_curve_unit_circle.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class SineCurveUnitCircle(Scene):
                # Full source: ~60 lines across show_axis(), show_circle(),
                # move_dot_and_draw_curve() with dt-based updaters and
                # always_redraw() for the radius line, connecting line, and curve.
                def construct(self):
                    self.show_axis()
                    self.show_circle()
                    self.move_dot_and_draw_curve()
                    self.wait()

----

Plotting
--------

.. admonition:: Example: SinAndCosFunctionPlot
   :class: example

   .. raw:: html

      <img src="_static/videos/sin_cos_plot.svg">

   Sine and cosine curves on shared axes.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/sin_cos_plot.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class SinAndCosFunctionPlot(Scene):
                def construct(self):
                    axes = Axes(
                        x_range=[-10, 10.3, 1], y_range=[-1.5, 1.5, 1],
                        x_length=10, axis_config={"color": GREEN},
                        x_axis_config={"numbers_to_include": np.arange(-10, 10.01, 2)},
                        tips=False,
                    )
                    sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
                    cos_graph = axes.plot(lambda x: np.cos(x), color=RED)
                    sin_label = axes.get_graph_label(sin_graph, r"\sin(x)", x_val=-10)
                    cos_label = axes.get_graph_label(cos_graph, label=r"\cos(x)")
                    self.add(axes, sin_graph, cos_graph, sin_label, cos_label)

.. admonition:: Example: ArgMinExample
   :class: example

   .. raw:: html

      <video src="_static/videos/arg_min.mp4" controls autoplay loop muted></video>

   A dot slides along a parabola to its minimum.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/arg_min.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class ArgMinExample(Scene):
                def construct(self):
                    ax = Axes(x_range=[0, 10], y_range=[0, 100, 10],
                              axis_config={"include_tip": False})
                    t = ValueTracker(0)
                    def func(x):
                        return 2 * (x - 5) ** 2
                    graph = ax.plot(func, color=MAROON)
                    initial_point = [ax.coords_to_point(t.get_value(), func(t.get_value()))]
                    dot = Dot(point=initial_point)
                    dot.add_updater(
                        lambda x: x.move_to(ax.c2p(t.get_value(), func(t.get_value())))
                    )
                    x_space = np.linspace(*ax.x_range[:2], 200)
                    minimum_index = func(x_space).argmin()
                    self.add(ax, graph, dot)
                    self.play(t.animate.set_value(x_space[minimum_index]))

.. admonition:: Example: GraphAreaPlot
   :class: example

   .. raw:: html

      <img src="_static/videos/graph_area_plot.svg">

   Shaded areas, vertical lines, and Riemann rectangles on a plot.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/graph_area_plot.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class GraphAreaPlot(Scene):
                def construct(self):
                    ax = Axes(x_range=[0, 5], y_range=[0, 6],
                              x_axis_config={"numbers_to_include": [2, 3]}, tips=False)
                    curve_1 = ax.plot(lambda x: 4 * x - x ** 2, x_range=[0, 4], color=BLUE_C)
                    curve_2 = ax.plot(
                        lambda x: 0.8 * x ** 2 - 3 * x + 4, x_range=[0, 4], color=GREEN_B
                    )
                    line_1 = ax.get_vertical_line(ax.input_to_graph_point(2, curve_1), color=YELLOW)
                    line_2 = ax.get_vertical_line(ax.i2gp(3, curve_1), color=YELLOW)
                    riemann_area = ax.get_riemann_rectangles(
                        curve_1, x_range=[0.3, 0.6], dx=0.03, color=BLUE, fill_opacity=0.5
                    )
                    area = ax.get_area(curve_2, [2, 3], bounded_graph=curve_1, color=GREY, opacity=0.5)
                    self.add(ax, curve_1, curve_2, line_1, line_2, riemann_area, area)

.. admonition:: Example: PolygonOnAxes
   :class: example

   .. raw:: html

      <video src="_static/videos/polygon_on_axes.mp4" controls autoplay loop muted></video>

   A rectangle's area tracks along a hyperbola as the width changes.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/polygon_on_axes.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class PolygonOnAxes(Scene):
                def construct(self):
                    ax = Axes(x_range=[0, 10], y_range=[0, 10], x_length=6, y_length=6,
                              axis_config={"include_tip": False})
                    t = ValueTracker(5)
                    k = 25
                    graph = ax.plot(lambda x: k / x, color=YELLOW_D,
                                    x_range=[k / 10, 10.0, 0.01], use_smoothing=False)
                    def get_rectangle():
                        polygon = Polygon(*[ax.c2p(*i) for i in
                            [(t.get_value(), k / t.get_value()), (0, k / t.get_value()),
                             (0, 0), (t.get_value(), 0)]])
                        polygon.set_fill(BLUE, opacity=0.5).set_stroke(YELLOW_B)
                        return polygon
                    polygon = always_redraw(get_rectangle)
                    dot = Dot()
                    dot.add_updater(lambda x: x.move_to(ax.c2p(t.get_value(), k / t.get_value())))
                    self.add(ax, graph, dot)
                    self.play(Create(polygon))
                    self.play(t.animate.set_value(10))
                    self.play(t.animate.set_value(k / 10))
                    self.play(t.animate.set_value(5))

.. admonition:: Example: HeatDiagramPlot
   :class: example

   .. raw:: html

      <img src="_static/videos/heat_diagram.svg">

   A line graph plotting temperature against heat with axis labels.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/heat_diagram.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class HeatDiagramPlot(Scene):
                def construct(self):
                    ax = Axes(
                        x_range=[0, 40, 5], y_range=[-8, 32, 5], x_length=9, y_length=6,
                        x_axis_config={"numbers_to_include": np.arange(0, 40, 5)},
                        y_axis_config={"numbers_to_include": np.arange(-5, 34, 5)},
                        tips=False,
                    )
                    labels = ax.get_axis_labels(
                        x_label=Tex(r"$\Delta Q$"), y_label=Tex(r"T[$^\circ C$]")
                    )
                    x_vals = [0, 8, 38, 39]
                    y_vals = [20, 0, 0, -5]
                    graph = ax.plot_line_graph(x_values=x_vals, y_values=y_vals)
                    self.add(ax, labels, graph)

----

Advanced
--------

.. admonition:: Example: GradientImageFromArray
   :class: example

   .. raw:: html

      <img src="_static/videos/gradient_image.svg">

   A black-to-white linear gradient with a green bounding rectangle.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/gradient_image.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class GradientImageFromArray(Scene):
                def construct(self):
                    n = 256
                    imageArray = np.uint8(
                        [[i * 256 / n for i in range(0, n)] for _ in range(0, n)]
                    )
                    image = ImageMobject(imageArray).scale(2)
                    image.background_rectangle = SurroundingRectangle(image, GREEN)
                    self.add(image, image.background_rectangle)

.. admonition:: Example: BooleanOperations
   :class: example

   .. raw:: html

      <video src="_static/videos/boolean_operations.mp4" controls autoplay loop muted></video>

   Boolean operations (intersection, union, exclusion, difference) on two overlapping ellipses.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/boolean_operations.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class BooleanOperations(Scene):
                def construct(self):
                    ellipse1 = Ellipse(
                        width=4.0, height=5.0, fill_opacity=0.5, color=BLUE, stroke_width=10
                    ).move_to(LEFT)
                    ellipse2 = Ellipse(
                        width=4.0, height=5.0, fill_opacity=0.5, color=RED, stroke_width=10
                    ).move_to(RIGHT)
                    bool_ops_text = MarkupText("<u>Boolean Operation</u>").next_to(ellipse1, UP * 3)
                    ellipse_group = Group(ellipse1, ellipse2)
                    self.play(FadeIn(ellipse_group))

                    i = Intersection(ellipse1, ellipse2, color=GREEN, fill_opacity=0.5)
                    self.play(i.animate.scale(0.25).move_to(RIGHT * 5 + UP * 2.5))
                    intersection_text = Text("Intersection", font_size=23).next_to(i, UP)
                    self.play(FadeIn(intersection_text))

                    u = Union(ellipse1, ellipse2, color=ORANGE, fill_opacity=0.5)
                    union_text = Text("Union", font_size=23)
                    self.play(u.animate.scale(0.3).next_to(i, DOWN, buff=union_text.height * 3))
                    union_text.next_to(u, UP)
                    self.play(FadeIn(union_text))

                    e = Exclusion(ellipse1, ellipse2, color=YELLOW, fill_opacity=0.5)
                    exclusion_text = Text("Exclusion", font_size=23)
                    self.play(e.animate.scale(0.3).next_to(u, DOWN, buff=exclusion_text.height * 3))
                    exclusion_text.next_to(e, UP)
                    self.play(FadeIn(exclusion_text))

                    d = Difference(ellipse1, ellipse2, color=PINK, fill_opacity=0.5)
                    difference_text = Text("Difference", font_size=23)
                    self.play(d.animate.scale(0.3).next_to(e, DOWN, buff=difference_text.height * 3))
                    difference_text.next_to(d, UP)
                    self.play(FadeIn(difference_text))

.. admonition:: Example: ZoomedInset
   :class: example

   .. raw:: html

      <video src="_static/videos/zoomed_inset_manim.mp4" controls autoplay loop muted></video>

   A zoomed inset magnifies a small region of the canvas.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/zoomed_inset_manim.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class MovingZoomedSceneAround(ZoomedScene):
                def __init__(self, **kwargs):
                    ZoomedScene.__init__(
                        self, zoom_factor=0.3,
                        zoomed_display_height=1, zoomed_display_width=6,
                        image_frame_stroke_width=20,
                        zoomed_camera_config={"default_frame_stroke_width": 3},
                        **kwargs
                    )

                def construct(self):
                    dot = Dot().shift(UL * 2)
                    image = ImageMobject(np.uint8([[0, 100, 30, 200], [255, 0, 5, 33]]))
                    image.height = 7
                    self.add(image, dot)
                    frame = self.zoomed_camera.frame
                    zoomed_display = self.zoomed_display
                    zoomed_display_frame = zoomed_display.display_frame
                    frame.move_to(dot)
                    frame.set_color(PURPLE)
                    zoomed_display_frame.set_color(RED)
                    zoomed_display.shift(DOWN)
                    zd_rect = BackgroundRectangle(zoomed_display, fill_opacity=0, buff=MED_SMALL_BUFF)
                    self.add_foreground_mobject(zd_rect)
                    unfold_camera = UpdateFromFunc(zd_rect, lambda rect: rect.replace(zoomed_display))
                    self.play(Create(frame))
                    self.activate_zooming()
                    self.play(self.get_zoomed_display_pop_out_animation(), unfold_camera)
                    self.play(frame.animate.shift(2.5 * DOWN + 4 * LEFT))
                    self.play(zoomed_display.animate.shift(2 * UP + 2 * RIGHT).scale(1.5))

----

3D
--

VectorMation renders 3D scenes using orthographic projection to SVG, with animatable camera angles (phi/theta), Lambertian shading, depth-sorted rendering, LaTeX axis labels, and filled surfaces with checkerboard colours.

.. admonition:: Example: FixedInFrameMObjectTest
   :class: example

   .. raw:: html

      <img src="_static/videos/three_d_axes.svg">

   Labeled 3D axes with a title.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/three_d_axes.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class FixedInFrameMObjectTest(ThreeDScene):
                def construct(self):
                    axes = ThreeDAxes()
                    self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
                    text3d = Text("This is a 3D text")
                    self.add_fixed_in_frame_mobjects(text3d)
                    text3d.to_corner(UL)
                    self.add(axes)

.. admonition:: Example: ThreeDSurfacePlot
   :class: example

   .. raw:: html

      <img src="_static/videos/three_d_surface_plot.svg">

   A Gaussian surface with checkerboard colours on 3D axes.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/three_d_surface_plot.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class ThreeDSurfacePlot(ThreeDScene):
                def construct(self):
                    resolution_fa = 24
                    self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES)
                    def param_gauss(u, v):
                        x, y = u, v
                        sigma, mu = 0.4, [0.0, 0.0]
                        d = np.sqrt((x - mu[0])**2 + (y - mu[1])**2)
                        z = np.exp(-(d**2 / (2.0 * sigma**2)))
                        return np.array([x, y, z])
                    gauss_plane = Surface(param_gauss,
                        resolution=(resolution_fa, resolution_fa),
                        v_range=[-2, +2], u_range=[-2, +2])
                    gauss_plane.scale(2, about_point=ORIGIN)
                    gauss_plane.set_style(fill_opacity=1, stroke_color=GREEN)
                    gauss_plane.set_fill_by_checkerboard(ORANGE, BLUE, opacity=0.5)
                    axes = ThreeDAxes()
                    self.add(axes, gauss_plane)

.. admonition:: Example: ThreeDLightSourcePosition
   :class: example

   .. raw:: html

      <img src="_static/videos/three_d_sphere.svg">

   A sphere with Lambertian shading and checkerboard colours on 3D axes.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/three_d_sphere.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class ThreeDLightSourcePosition(ThreeDScene):
                def construct(self):
                    axes = ThreeDAxes()
                    sphere = Surface(
                        lambda u, v: np.array([
                            1.5 * np.cos(u) * np.cos(v),
                            1.5 * np.cos(u) * np.sin(v),
                            1.5 * np.sin(u)
                        ]), v_range=[0, TAU], u_range=[-PI / 2, PI / 2],
                        checkerboard_colors=[RED_D, RED_E], resolution=(15, 32))
                    self.renderer.camera.light_source.move_to(3 * IN)
                    self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                    self.add(axes, sphere)

.. admonition:: Example: ThreeDCameraRotation
   :class: example

   .. raw:: html

      <video src="_static/videos/three_d_camera.mp4" controls autoplay loop muted></video>

   A saddle surface with the camera rotating 360 degrees.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/three_d_camera.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class ThreeDCameraRotation(ThreeDScene):
                def construct(self):
                    axes = ThreeDAxes()
                    self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
                    self.add(axes)
                    self.begin_ambient_camera_rotation(rate=0.1)
                    self.wait(6)

.. admonition:: Example: ParametricCurve3DExample
   :class: example

   .. raw:: html

      <img src="_static/videos/three_d_helix.svg">

   A helix drawn as a parametric curve in 3D space.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/three_d_helix.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class ParametricCurve3DExample(ThreeDScene):
                def construct(self):
                    axes = ThreeDAxes()
                    self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
                    curve = ParametricFunction(
                        lambda t: np.array([np.cos(t), np.sin(t), t / (2 * PI)]),
                        t_range=[0, 4 * PI], color=YELLOW
                    )
                    dot = Dot3D(axes.c2p(1, 0, 0), color=RED)
                    self.add(axes, curve, dot)

.. admonition:: Example: FollowingGraphCamera
   :class: example

   .. raw:: html

      <video src="_static/videos/following_graph_camera.mp4" controls autoplay loop muted></video>

   Camera zooms in and follows a dot sliding along a sine curve.

   .. tab-set::

      .. tab-item:: VectorMation

         .. literalinclude:: ../../examples/manim/following_graph_camera.py
            :language: python

      .. tab-item:: Manim

         .. code-block:: python

            class FollowingGraphCamera(MovingCameraScene):
                def construct(self):
                    self.camera.frame.save_state()
                    ax = Axes(x_range=[-1, 10], y_range=[-1, 10])
                    graph = ax.plot(lambda x: np.sin(x), color=BLUE,
                                    x_range=[0, 3 * PI])
                    dot = Dot(ax.i2gp(0, graph), color=ORANGE)
                    self.add(ax, graph, dot)
                    self.play(self.camera.frame.animate.scale(0.5).move_to(dot))
                    def update_camera(mob):
                        mob.move_to(dot.get_center())
                    self.camera.frame.add_updater(update_camera)
                    self.play(MoveAlongPath(dot, graph, rate_func=linear),
                              run_time=8)
                    self.camera.frame.remove_updater(update_camera)
                    self.play(Restore(self.camera.frame))

----

Summary
-------

VectorMation recreates **all 25** Manim example gallery scenes.

VectorMation replaces Manim's imperative ``self.play()`` pattern with a **declarative, time-based** approach. Animations are defined by their time interval and the library can render any frame instantly. This makes iteration faster (browser hot-reload) and code shorter (no ceremony of classes and play calls).
