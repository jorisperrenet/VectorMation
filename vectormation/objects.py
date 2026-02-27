"""Re-export module: imports all public names from sub-modules.

The actual implementations live in:
  _constants.py      — size/direction constants, helper functions
  _base.py           — VObject (base class), VCollection, VGroup
  _canvas.py         — VectorMathAnim (canvas/video)
  _shapes.py         — basic shapes (Polygon, Circle, Rectangle, Line, Text, Arc, etc.)
  _arrows.py         — Arrow, DoubleArrow, CurvedArrow, Brace
  _axes.py           — Axes, Graph, NumberPlane, ComplexPlane
  _composites.py     — remaining composites (NumberLine, Table, etc.)
  _charts.py         — chart/visualization classes (PieChart, BarChart, etc.)
  _diagrams.py       — diagram classes (Tree, FlowChart, NetworkGraph, etc.)
  _ui.py             — UI component classes (TextBox, Badge, etc.)
  _data_structures.py — data structure visualizations (Array, Stack, etc.)
  _science.py        — science/electronics classes (Resistor, NeuralNetwork, etc.)
  _svg_utils.py      — SVG utilities, boolean ops (from_svg, Union, etc.)
  _threed.py         — 3D objects (ThreeDAxes, Surface, Line3D, Dot3D, etc.)
"""
# Re-export everything so `from vectormation.objects import X` still works.

from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT,
    UNIT, SMALL_BUFF, MED_SMALL_BUFF, MED_LARGE_BUFF, LARGE_BUFF,
    DEFAULT_STROKE_WIDTH, DEFAULT_FONT_SIZE, DEFAULT_DOT_RADIUS, DEFAULT_SMALL_DOT_RADIUS,
    DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    DEFAULT_OBJECT_TO_EDGE_BUFF, DEFAULT_OBJECT_TO_OBJECT_BUFF,
    DEFAULT_CHART_COLORS, CHAR_WIDTH_FACTOR, TEXT_Y_OFFSET,
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR, ORIGIN,
    interpolate_value, smooth_index,
)

from vectormation._base import VObject, VCollection, VGroup

from vectormation._canvas import VectorMathAnim

from vectormation._shapes import (
    Polygon, Ellipse, Circle, Dot, AnnotationDot, Rectangle, RoundedRectangle,
    Line, DashedLine, Lines, FunctionGraph,
    Text, CountAnimation, ValueTracker, DecimalNumber,
    Path, Image, Trace,
    RegularPolygon, Star, EquilateralTriangle,
    Arc, Wedge, Annulus,
    ArcBetweenPoints, Elbow, AnnularSector,
    CubicBezier, Paragraph, BulletedList, NumberedList,
    SurroundingRectangle, SurroundingCircle, BackgroundRectangle, ScreenRectangle,
)
# Aliases
Sector = Wedge
Triangle = EquilateralTriangle

from vectormation._arrows import Arrow, DoubleArrow, CurvedArrow, Brace, Vector

from vectormation._axes import Axes, Graph, NumberPlane, ComplexPlane
from vectormation._axes_helpers import pi_format, pi_ticks

from vectormation._composites import (
    MorphObject, LabeledDot, TexObject, SplitTexObject,
    TexCountAnimation, ParametricFunction,
    NumberLine, Table, Matrix,
    DynamicObject,
    always_redraw, parse_args,
)

from vectormation._svg_utils import (
    ClipPath, BlurFilter, DropShadowFilter,
    Angle, RightAngle, Cross,
    ZoomedInset,
    Union, Difference, Intersection, Exclusion,
    brace_between_points,
    ArrowVectorField, StreamLines, Cutout,
    from_svg, from_svg_file, _parse_inline_style,
)

from vectormation._charts import (
    PieChart, DonutChart, BarChart,
    PolarAxes, Legend,
    RadarChart, ProgressBar,
    SampleSpace,
    WaterfallChart, GanttChart, SankeyDiagram,
    FunnelChart, TreeMap, GaugeChart, SparkLine,
    KPICard, BulletChart, CalendarHeatmap,
    WaffleChart,
    CircularProgressBar, Scoreboard,
    MatrixHeatmap, BoxPlot,
)

from vectormation._diagrams import (
    ChessBoard, PeriodicTable, BohrAtom, Automaton,
    NetworkGraph, Tree, Stamp, TimelineBar,
    FlowChart, VennDiagram, OrgChart, MindMap,
)

from vectormation._ui import (
    Title, Variable, Underline, Code,
    Label, LabeledLine, LabeledArrow,
    Callout, DimensionLine, Tooltip,
    TextBox, Bracket, IconGrid,
    SpeechBubble, Badge, Divider,
    Checklist, Stepper, TagCloud,
    StatusIndicator, Meter, Breadcrumb,
    Countdown, Filmstrip,
    RoundedCornerPolygon,
)

from vectormation._data_structures import (
    Array, Stack, Queue, LinkedList, BinaryTree,
    ArrayViz, LinkedListViz, StackViz, QueueViz,
    _flash_fill,
)

from vectormation._science import (
    Resistor, Capacitor, Inductor, Diode, LED, UnitInterval, Molecule2D,
    NeuralNetwork, Pendulum, StandingWave,
)

from vectormation.colors import (LinearGradient, RadialGradient,
    color_gradient, interpolate_color, lighten, darken,
    adjust_hue, saturate, desaturate, complementary,
    set_saturation, set_lightness, invert,
    triadic, analogous, split_complementary)

from vectormation._threed import (
    ThreeDAxes, Surface, Sphere3D, Cube,
    Line3D, Arrow3D, Dot3D, ParametricCurve3D, Text3D,
    Cylinder3D, Cone3D, Torus3D, Prism3D,
)
