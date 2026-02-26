"""Re-export module: imports all public names from sub-modules.

The actual implementations live in:
  _constants.py  — size/direction constants, helper functions
  _base.py       — VObject (base class), VCollection, VGroup
  _canvas.py     — VectorMathAnim (canvas/video)
  _shapes.py     — basic shapes (Polygon, Circle, Rectangle, Line, Text, Arc, etc.)
  _composites.py — composites (Arrow, Axes, Graph, NumberLine, Table, etc.)
  _threed.py     — 3D objects (ThreeDAxes, Surface, Line3D, Dot3D, etc.)
"""
# Re-export everything so `from vectormation.objects import X` still works.

from vectormation._constants import (
    UNIT, SMALL_BUFF, MED_SMALL_BUFF, MED_LARGE_BUFF, LARGE_BUFF,
    DEFAULT_STROKE_WIDTH, DEFAULT_FONT_SIZE, DEFAULT_DOT_RADIUS, DEFAULT_SMALL_DOT_RADIUS,
    DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    DEFAULT_OBJECT_TO_EDGE_BUFF, DEFAULT_OBJECT_TO_OBJECT_BUFF,
    DEFAULT_CHART_COLORS, CHAR_WIDTH_FACTOR, TEXT_Y_OFFSET,
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR, ORIGIN,
)

from vectormation._base import VObject, VCollection, VGroup, _make_brect

from vectormation._canvas import VectorMathAnim

from vectormation._shapes import (
    Polygon, Ellipse, Circle, Dot, Rectangle, RoundedRectangle,
    Line, DashedLine, Lines, FunctionGraph,
    Text, CountAnimation, ValueTracker, DecimalNumber,
    Path, Image, Trace,
    RegularPolygon, Star, EquilateralTriangle,
    Arc, Wedge, Annulus,
    ArcBetweenPoints, Elbow, AnnularSector,
    CubicBezier, Paragraph, BulletedList, NumberedList,
    SurroundingRectangle, SurroundingCircle, BackgroundRectangle, ScreenRectangle,
)
# Alias
Sector = Wedge

from vectormation._composites import (
    MorphObject, LabeledDot, TexObject, SplitTexObject,
    Axes, Graph, NumberPlane,
    Arrow, DoubleArrow, CurvedArrow, Brace,
    ClipPath, BlurFilter, DropShadowFilter,
    Angle, RightAngle, Cross, NumberLine,
    PieChart, DonutChart, BarChart, Table, Matrix,
    DynamicObject, ZoomedInset,
    Union, Difference, Intersection, Exclusion,
    Title,
    Variable, Underline, brace_between_points,
    ArrowVectorField, ComplexPlane, Code,
    ChessBoard, PeriodicTable, BohrAtom, Automaton,
    NetworkGraph,
    Label, LabeledArrow, StreamLines, PolarAxes,
    Callout, DimensionLine, Tooltip, Tree,
    Stamp, TimelineBar, Legend, RadarChart, ProgressBar, FlowChart,
    WaterfallChart, GanttChart, SankeyDiagram,
    FunnelChart, TreeMap, GaugeChart, SparkLine,
    VennDiagram, OrgChart,
    KPICard, BulletChart, CalendarHeatmap,
    WaffleChart, MindMap,
    CircularProgressBar, Scoreboard,
    MatrixHeatmap, BoxPlot, TextBox, Bracket, IconGrid,
    SpeechBubble, Badge, Divider,
    Checklist, Stepper, TagCloud,
    StatusIndicator, Meter, Breadcrumb,
    Countdown, Filmstrip,
    SampleSpace, RoundedCornerPolygon,
    Array, Stack, Queue, LinkedList, BinaryTree,
    Resistor, Capacitor, Inductor, Diode, LED, UnitInterval, Molecule2D,
    from_svg, from_svg_file, always_redraw, parse_args,
    _parse_inline_style,
)

from vectormation.colors import (LinearGradient, RadialGradient,
    color_gradient, interpolate_color, lighten, darken,
    adjust_hue, saturate, desaturate, complementary,
    set_saturation, set_lightness, invert)

from vectormation._threed import (
    ThreeDAxes, Surface, Sphere3D, Cube,
    Line3D, Arrow3D, Dot3D, ParametricCurve3D, Text3D,
    Cylinder3D, Cone3D, Torus3D, Prism3D,
)
