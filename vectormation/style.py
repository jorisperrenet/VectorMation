import vectormation.attributes as attributes
import vectormation.easings as easings


class Styling:
    """Represents the styling part of an svg"""
    # Define the attributes that this class will have (and their respective type)
    styles = ['opacity', 'fill', 'fill_opacity', 'stroke', 'stroke_width', 'stroke_opacity',
              'fill_rule', 'stroke_dasharray', 'stroke_linecap', 'stroke_linejoin']
    transforms = ['scale_x', 'scale_y', 'dx', 'dy', 'skew_x',
                  'skew_y', 'rotation', 'skew_x_after', 'skew_y_after', 'matrix']

    def __init__(self, kwargs, creation=0, **defaults):
        # We take the shape-specific defaults and let them overwrite the global defaults
        # We take the kwargs (specified by the person animating) and let them overwrite the shape-specific defaults
        self.kw = kwargs
        self.defaults = defaults
        self.global_defaults = dict(
            opacity = 1,
            fill = '#000',
            fill_opacity = 1,
            stroke = '#000',
            stroke_width = 1,
            stroke_opacity = 1,
            fill_rule = 'nonzero',
            stroke_dasharray = '',
            stroke_linecap = 'butt',
            stroke_linejoin = 'miter',  # arcs | bevel | miter | miter-clip | round
            ### Transformations
            scale_x = 1,
            scale_y = 1,
            dx = 0,
            dy = 0,
            skew_x = 0,
            skew_y = 0,
            rotation = (0, 0, 0),
            skew_x_after = 0,
            skew_y_after = 0,
            matrix = (0, 0, 0, 0, 0, 0),
        )

        # Check for unknown specified kwargs/shape-specific defaults
        assert all(arg in self.global_defaults for arg in self.kw)  # unknown arguments passed
        assert all(arg in self.global_defaults for arg in self.defaults)
        assert all(arg in self.global_defaults for arg in self.styles + self.transforms)
        assert all((arg in self.styles) ^ (arg in self.transforms) for arg in self.global_defaults)

        # Set the values from the creation time of this Styling class onwards
        self.set_values(creation=creation, **(self.global_defaults | self.defaults | self.kw))

    def set_values(self, creation=0, **values):
        """Sets the values of the global defaults starting at the creation"""
        self.opacity            = attributes.Real(creation, values['opacity'])
        self.fill               = attributes.Color(creation, values['fill'])
        self.fill_opacity       = attributes.Real(creation, values['fill_opacity'])
        self.stroke             = attributes.Color(creation, values['stroke'])
        self.stroke_width       = attributes.Real(creation, values['stroke_width'])
        self.stroke_opacity     = attributes.Real(creation, values['stroke_opacity'])
        self.fill_rule          = attributes.String(creation, values['fill_rule'])
        self.stroke_dasharray   = attributes.String(creation, values['stroke_dasharray'])
        self.stroke_linecap     = attributes.String(creation, values['stroke_linecap'])
        self.stroke_linejoin    = attributes.String(creation, values['stroke_linejoin'])
        ### Transformations
        self.scale_x            = attributes.Real(creation, values['scale_x'])
        self.scale_y            = attributes.Real(creation, values['scale_y'])
        self.dx                 = attributes.Real(creation, values['dx'])
        self.dy                 = attributes.Real(creation, values['dy'])
        self.skew_x             = attributes.Real(creation, values['skew_x'])
        self.skew_y             = attributes.Real(creation, values['skew_y'])
        self.rotation           = attributes.Tup(creation, values['rotation'])
        self.skew_x_after       = attributes.Real(creation, values['skew_x_after'])
        self.skew_y_after       = attributes.Real(creation, values['skew_y_after'])
        self.matrix             = attributes.Tup(creation, values['matrix'])

    def kwargs(self):
        """Returns the key-word arguments specifying the styling as functions of time (attributes)"""
        return {attr: getattr(self, attr) for attr in self.global_defaults}

    @property
    def last_change(self):
        """Returns the last change of any attribute contained in this class"""
        return max(val.last_change for val in self.kwargs().values())

    def svg_style(self, time):
        """Returns the style part of the svg object"""
        # To avoid redundancy we only write each value if it is not equal to the global default value
        args = {arg: getattr(self, arg).at_time(time) for arg in self.styles}

        string = ''
        # Iterate through the pairs of names vs stylenames (the name in the svg style part)
        for name, stylename in [('opacity', 'opacity'), ('fill', 'fill'), ('fill_opacity', 'fill-opacity'),
                                ('stroke', 'stroke'), ('stroke_width', 'stroke-width'),
                                ('stroke_opacity', 'stroke-opacity'), ('fill_rule', 'fill-rule'),
                                ('stroke_dasharray', 'stroke-dasharray'), ('stroke_linecap', 'stroke-linecap'),
                                ('stroke_linejoin', 'stroke-linejoin')]:
            if args[name] != self.global_defaults[name]:
                string += f" {stylename}='{args[name]}'"

        # Now, we do the transform argument
        transform = self.transform_style(time)
        if transform != '':
            string += f" transform='{transform[1:]}'"

        return string

    def transform_style(self, time):
        """Returns the transform style argument of the styling of the svg object"""
        args = {arg: getattr(self, arg).at_time(time) for arg in self.transforms}

        transform = ''
        if not args['dx'] == args['dy'] == self.global_defaults['dx'] == self.global_defaults['dy']:
            transform += f" translate({args['dx']},{args['dy']})"
        if not args['scale_x'] == args['scale_y'] == self.global_defaults['scale_x'] == self.global_defaults['scale_y']:
            transform += f" scale({args['scale_x']},{args['scale_y']})"
        if not args['skew_x'] == self.global_defaults['skew_x']:
            transform += f" skewX({args['skew_x']})"
        if not args['skew_y'] == self.global_defaults['skew_y']:
            transform += f" skewY({args['skew_y']})"
        if not args['rotation'] == self.global_defaults['rotation']:
            r, x, y = args['rotation']
            transform += f" rotate({r%360},{x},{y})"
        if not args['skew_x_after'] == self.global_defaults['skew_x_after']:
            transform += f" skewX({args['skew_x_after']})"
        if not args['skew_y_after'] == self.global_defaults['skew_y_after']:
            transform += f" skewY({args['skew_y_after']})"
        if not args['matrix'] == self.global_defaults['matrix']:
            a, b, c, d, e, f = args['matrix']
            transform += f" matrix({a},{b},{c},{d},{e},{f})"
        return transform

    def interpolate(self, other, start, end, easing=easings.linear):
        """Interpolate all styling values from self at time start to other at time end with easing"""
        assert isinstance(other, Styling)
        # If all values are the same, i.e. the class is exactly the same, we do not need to change
        # anyting, thus return the current values.
        if self == other:
            # NOTE: TODO: also add the rotation to the fade-in objects here
            # inter_attr = self.rotation.interpolate(attributes.Tup(0, (360, 0, 0)), start, end, easing=easing)
            # self.rotation = inter_attr
            return self

        # We create a new styling class as the interpolated styling
        new_styling = Styling({}, creation=start)
        # We need to interpolate all the values of both styling classes
        # The Real attributes are easily interpolated, some others must be set at once.
        for attr in self.transforms + self.styles:
            start_attr = getattr(self, attr)
            end_attr = getattr(other, attr)
            start_val = start_attr.at_time(start)
            end_val = end_attr.at_time(end)
            if start_val == end_val:
                # if attr == 'rotation':
                #     # NOTE: TODO: add 360 degrees but rotate around the center of the object
                #     inter_attr = start_attr.interpolate(attributes.Tup(0, (360, 0, 0)), start, end, easing=easing)
                #     setattr(new_styling, attr, inter_attr)
                #     print(start_val, end_val)
                #     continue
                # We do not need to transform anything
                getattr(new_styling, attr).set(start, end, start_attr.time_func)
                continue
            # If the values are unequal we need to interpolate these values
            inter_attr = start_attr.interpolate(end_attr, start, end, easing=easing)
            setattr(new_styling, attr, inter_attr)
        # NOTE: TODO: add rotation argument that rotaetes the objects a full circle.
        return new_styling
