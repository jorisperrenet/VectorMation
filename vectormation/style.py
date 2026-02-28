"""Styling system for SVG presentation attributes and transforms.

Each VObject has a Styling instance controlling its visual appearance (fill, stroke, opacity, etc.)
and geometric transforms (translate, scale, rotate, skew). All values are time-varying attributes.
"""
import vectormation.attributes as attributes
import vectormation.easings as easings


# Schema: (attr_name, svg_name_or_None, attr_class, default_value, svg_default)
# svg_name=None means it's a transform-only attribute (not in style output).
# svg_default is the SVG spec default (what the browser assumes when the attribute
# is omitted). None means the attribute is always emitted.
_ATTR_SCHEMA = [
    # Styles                                                        vm default  svg default
    ('opacity',            'opacity',           attributes.Real,   1,           1),
    ('fill',               'fill',              attributes.Color,  '#000',      '#000'),
    ('fill_opacity',       'fill-opacity',      attributes.Real,   1,           1),
    ('stroke',             'stroke',            attributes.Color,  '#000',      None),
    ('stroke_width',       'stroke-width',      attributes.Real,   4,           1),
    ('stroke_opacity',     'stroke-opacity',    attributes.Real,   1,           1),
    ('fill_rule',          'fill-rule',         attributes.String, 'nonzero',   'nonzero'),
    ('stroke_dasharray',   'stroke-dasharray',  attributes.String, '',          ''),
    ('stroke_dashoffset',  'stroke-dashoffset', attributes.Real,   0,           0),
    ('stroke_linecap',     'stroke-linecap',    attributes.String, 'butt',      'butt'),
    ('stroke_linejoin',    'stroke-linejoin',   attributes.String, 'miter',     'miter'),
    ('clip_path',          'clip-path',         attributes.String, '',          ''),
    # Transforms (svg_name=None)
    ('scale_x',       None, attributes.Real, 1,              None),
    ('scale_y',       None, attributes.Real, 1,              None),
    ('dx',            None, attributes.Real, 0,              None),
    ('dy',            None, attributes.Real, 0,              None),
    ('skew_x',        None, attributes.Real, 0,              None),
    ('skew_y',        None, attributes.Real, 0,              None),
    ('rotation',      None, attributes.Tup,  (0, 0, 0),     None),
    ('skew_x_after',  None, attributes.Real, 0,              None),
    ('skew_y_after',  None, attributes.Real, 0,              None),
    ('matrix',        None, attributes.Tup,  (0, 0, 0, 0, 0, 0), None),
]

# Derived lookups
_STYLE_PAIRS = [(name, svg) for name, svg, _, _, _ in _ATTR_SCHEMA if svg is not None]
_STYLES = [name for name, svg, _, _, _ in _ATTR_SCHEMA if svg is not None]
_GLOBAL_DEFAULTS = {name: default for name, _, _, default, _ in _ATTR_SCHEMA}
_ATTR_NAMES = [name for name, _, _, _, _ in _ATTR_SCHEMA]

# Pre-render SVG spec defaults for style comparison (computed once at import).
# None means the attribute is always emitted (no SVG spec default to match).
_RENDERED_DEFAULTS = {name: cls(0, svg_default).at_time(0) if svg_default is not None else None
                      for name, svg, cls, _, svg_default in _ATTR_SCHEMA if svg is not None}


class Styling:
    """Represents the styling part of an svg."""
    global_defaults = _GLOBAL_DEFAULTS

    # Styles
    opacity: attributes.Real
    fill: attributes.Color
    fill_opacity: attributes.Real
    stroke: attributes.Color
    stroke_width: attributes.Real
    stroke_opacity: attributes.Real
    fill_rule: attributes.String
    stroke_dasharray: attributes.String
    stroke_dashoffset: attributes.Real
    stroke_linecap: attributes.String
    stroke_linejoin: attributes.String
    clip_path: attributes.String
    # Transforms
    scale_x: attributes.Real
    scale_y: attributes.Real
    dx: attributes.Real
    dy: attributes.Real
    skew_x: attributes.Real
    skew_y: attributes.Real
    rotation: attributes.Tup
    skew_x_after: attributes.Real
    skew_y_after: attributes.Real
    matrix: attributes.Tup

    def __init__(self, kwargs, creation: float = 0, **defaults):
        assert all(arg in self.global_defaults for arg in kwargs)
        assert all(arg in self.global_defaults for arg in defaults)
        self.set_values(creation=creation, **(self.global_defaults | defaults | kwargs))
        self._scale_origin: tuple[float, float] | None = None

    def set_values(self, creation: float = 0, **values):
        for name, _, cls, _, _ in _ATTR_SCHEMA:
            setattr(self, name, cls(creation, values[name]))

    def kwargs(self):
        return {name: getattr(self, name) for name in _ATTR_NAMES}

    @property
    def last_change(self):
        return max(getattr(self, name).last_change for name in _ATTR_NAMES)

    def svg_style(self, time):
        string = ''
        for name, stylename in _STYLE_PAIRS:
            val = getattr(self, name).at_time(time)
            rendered_default = _RENDERED_DEFAULTS[name]
            if rendered_default is None or val != rendered_default:
                string += f" {stylename}='{val}'"

        transform = self.transform_style(time)
        if transform:
            string += f" transform='{transform}'"

        return string

    def transform_style(self, time):
        parts = []
        rot = self.rotation.at_time(time)
        if rot != (0, 0, 0):
            parts.append(f'rotate({-rot[0]%360},{rot[1]},{rot[2]})')
        dx, dy = self.dx.at_time(time), self.dy.at_time(time)
        if dx != 0 or dy != 0:
            parts.append(f'translate({dx},{dy})')
        sx, sy = self.scale_x.at_time(time), self.scale_y.at_time(time)
        if sx != 1 or sy != 1:
            if self._scale_origin:
                cx, cy = self._scale_origin
                parts.append(f'translate({cx},{cy}) scale({sx},{sy}) translate({-cx},{-cy})')
            else:
                parts.append(f'scale({sx},{sy})')
        skx = self.skew_x.at_time(time)
        if skx != 0:
            parts.append(f'skewX({skx})')
        sky = self.skew_y.at_time(time)
        if sky != 0:
            parts.append(f'skewY({sky})')
        skxa = self.skew_x_after.at_time(time)
        if skxa != 0:
            parts.append(f'skewX({skxa})')
        skya = self.skew_y_after.at_time(time)
        if skya != 0:
            parts.append(f'skewY({skya})')
        mat = self.matrix.at_time(time)
        if mat != (0, 0, 0, 0, 0, 0):
            parts.append(f"matrix({','.join(str(v) for v in mat)})")
        return ' '.join(parts)

    def interpolate(self, other, start, end, easing=easings.linear,
                    rotation_degrees=0, rotation_center=None):
        assert isinstance(other, Styling)
        if self == other and rotation_degrees == 0:
            return self

        if rotation_center is None:
            rotation_center = (0, 0)

        new_styling = Styling({}, creation=start)
        for attr in _ATTR_NAMES:
            start_attr = getattr(self, attr)
            end_attr = getattr(other, attr)
            start_val = start_attr.at_time(start)
            end_val = end_attr.at_time(end)

            if attr == 'rotation' and rotation_degrees != 0:
                rcx, rcy = rotation_center
                rot_start = (start_val[0], rcx, rcy)
                rot_end = (end_val[0] + rotation_degrees, rcx, rcy)
                start_tup = attributes.Tup(0, rot_start)
                start_tup.last_change = start
                end_tup = attributes.Tup(0, rot_end)
                end_tup.last_change = end
                inter_attr = start_tup.interpolate(end_tup, start, end, easing=easing)
                setattr(new_styling, attr, inter_attr)
                continue

            if start_val == end_val:
                getattr(new_styling, attr).set(start, end, start_attr.time_func)
                continue
            inter_attr = start_attr.interpolate(end_attr, start, end, easing=easing)
            setattr(new_styling, attr, inter_attr)
        return new_styling
