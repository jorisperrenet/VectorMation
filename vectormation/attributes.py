import math
import vectormation.colors as colors
import vectormation.easings as easings

def sigmoid(x):
  return 1 / (1 + math.exp(-x))


def heaviside(time, if_equal=1):
    """Returns a heaviside/step function being 0 if x < time and 1 if x > time"""
    return lambda x: 1 if x > time else 0 if x < time else if_equal


class Real:
    """The real attribute is a real-valued attribute (changing) through time"""
    def __init__(self, creation, start_val=0):
        if isinstance(start_val, Real):
            self.set_to(start_val)
        else:
            # Define the function
            self.time_func = lambda t: heaviside(creation)(t) * start_val
            # Define the last change time of this attribute (after that it's constant)
            self.last_change = creation

    def set(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Set this attribute to func_inner(x) on [start, end]
        lincl, rincl are if the brackets are [/] or (/)"""
        func_outer = self.time_func
        def new_func(t):
            if t < start: return func_outer(t)
            elif t > end:
                if stay: return new_func(end)
                else: return func_outer(t)
            elif not lincl and t == start: return func_outer(t)
            elif not rincl and t == end: return func_outer(t)
            else: return func_inner(t)
        self.time_func = new_func
        self.last_change = max(self.last_change, end)

    def add(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Set this attribute to func_inner(x)+previous on [start, end]
        lincl, rincl are if the brackets are [/] or (/)"""
        func_outer = self.time_func
        def new_func(t):
            if t < start: return func_outer(t)
            elif t > end:
                if stay: return new_func(end)
                else: return func_outer(t)
            elif not lincl and t == start: return func_outer(t)
            elif not rincl and t == end: return func_outer(t)
            else: return float(func_outer(t)) + func_inner(t)
        self.time_func = new_func
        self.last_change = max(self.last_change, end)

    def set_onward(self, start, value, lincl=True):
        """Set this attribute to value on [start, infty]
        lincl are if the bracket is [/] or (/)"""
        func_left = self.time_func
        def new_func(t):
            if t < start: return func_left(t)
            elif not lincl and t == start: return func_left(t)
            else:
                if callable(value): return value(t)
                else: return value
        self.time_func = new_func
        self.last_change = max(self.last_change, start)

    def add_onward(self, start, func, lincl=True, last_change=None):
        """Set this attribute to value + func(val) on [start, infty]
        lincl are if the bracket is [/] or (/)"""
        func_left = self.time_func
        def new_func(t):
            if t < start: return func_outer(t)
            elif not lincl and t == start: return func_left(t)
            else:
                if callable(func): return float(func_left(t)) + func(t)
                else: return float(func_left(t)) + func
        self.time_func = new_func
        self.last_change = max(self.last_change, start)
        if last_change != None:
            self.last_change = max(self.last_change, last_change)


    def set_at(self, time, value):
        """Set this attribute to value on time
        lincl are if the bracket is [/] or (/)"""
        func_otherwise = self.time_func
        def new_func(t):
            if t == time: return value
            else: return func_otherwise(t)
        self.time_func = new_func
        self.last_change = max(self.last_change, time)

    def add_at(self, time, value, default=0):
        """Set this attribute to the value + the value before on time
        If the value is none, set to default.
        lincl are if the bracket is [/] or (/)"""
        old = float(self.time_func(time))
        if old == None:
            old = default
        func_otherwise = self.time_func
        def new_func(t):
            if t == time: return old + value
            else: return func_otherwise(t)
        self.time_func = new_func
        self.last_change = max(self.last_change, time)

    def at_time(self, time):
        return self.time_func(time)

    def set_to(self, other):
        """Set the value of self to always be the value of other"""
        # The value needs to update as the time_function updates
        self.time_func = lambda t: other.time_func(t)
        self.last_change = other.last_change

    def move_to(self, start_time, end_time, end_val, stay=True, easing=easings.smooth):
        """Animate the object going from start_pos to end_pos, exponentially"""
        start_val = self.time_func(start_time)
        diff = start_val - end_val
        s, e = start_time, end_time
        self.set(s, e, lambda t: diff * (1-easing((t-s)/(e-s))) + end_val, stay=stay)
        self.last_change = max(self.last_change, end_time)

    def interpolate(self, other, start, end, easing=easings.linear):
        """Interpolate this value from start to end with easing to the other value
        Return a lambda function (or this same attribute) for these times"""
        assert self.__class__ == Real  # Both classes need to be a real object
        assert other.__class__ == Real
        start_val = self.time_func(start)
        end_val = other.time_func(end)
        # We need to get from start_val to end_val with easing
        s, e = start, end

        new = Real(0)
        new.time_func = lambda t: start_val + (end_val-start_val) * easing((t-s)/(e-s))
        new.last_change = end
        return new


class Natural(Real):
    """A natural number"""
    def at_time(self, time, rounding_func=round):
        """Get the value at some time"""
        return rounding_func(self.time_func(time))


class Tup(Real):
    """Arbitrary length real attribute"""
    def __init__(self, creation, start_val):
        if isinstance(start_val, Tup):
            self.set_to(start_val)
        else:
            # Define the function
            self.time_func = lambda t: tuple(
                    [heaviside(creation)(t) * val for val in start_val]
                )
            # Define the last change time of this attribute (after that it's constant)
            self.last_change = creation

    def add(self, start, end, value, lincl=True, rincl=True, stay=False):
        """Set this attribute to value+previous on [start, end]
        lincl, rincl are if the brackets are [/] or (/)"""
        # NOTE: TODO: complete rewrite maybe with an Attribute class
        func_outer = self.time_func
        def new_func(t):
            if t < start: return func_outer(t)
            elif t > end:
                if stay: return new_func(end)
                else: return func_outer(t)
            elif not lincl and t == start: return func_outer(t)
            elif not rincl and t == end: return func_outer(t)
            else: return tuple(float(i) + value[idx] for idx, i in enumerate(func_outer(t)))
        self.time_func = new_func
        self.last_change = max(self.last_change, end)

    def interpolate(self, other, start, end, easing=easings.smooth):
        """Interpolate this value from start to end with easing to the other value
        Return a lambda function (or this same attribute) for these times"""
        assert self.__class__ == Tup  # Both classes need to be a real object
        assert other.__class__ == Tup
        start_val = self.time_func(start)
        end_val = other.time_func(end)
        # We need to get from start_val to end_val with easing
        new = Tup(0, ())
        new.time_func = lambda t: tuple(s + (e-s) * easing((t-start)/(end-start)) for s, e in zip(start_val, end_val))
        new.last_change = end
        return new



class Coor(Real):
    """The coordinate attribute is a real-valued attribute (changing) through time"""
    def __init__(self, creation, start_val=(0, 0)):
        # Define the function
        self.time_func = lambda t: (
                heaviside(creation)(t) * start_val[0],
                heaviside(creation)(t) * start_val[1],
            )
        # Define the last change time of this attribute (after that it's constant)
        self.last_change = creation

    def add_onward(self, start, func, lincl=True, last_change=None):
        """Set this attribute to value + func(val) on [start, infty]
        lincl are if the bracket is [/] or (/)"""
        func_left = self.time_func
        def new_func(t):
            if t < start: return func_outer(t)
            elif not lincl and t == start: return func_left(t)
            else:
                if callable(func): return (func_left(t)[0] + func(t)[0], func_left(t)[1] + func(t)[1])
                else: return (func_left(t)[0] + func[0], func_left(t)[1] + func[1])
        self.time_func = new_func
        self.last_change = max(self.last_change, start)
        if last_change != None:
            self.last_change = max(self.last_change, last_change)

    def rotate_around(self, start_time, end_time, pivot_point, degrees, clockwise=False, stay=True):
        """Animate the object going from pivoting around the pivot point counterclockwise"""
        # NOTE: TODO: allow pivot_point to be a function
        old_func = self.time_func
        def f(t):
            now = old_func(t)
            rel_pos = (now[0] - pivot_point[0], now[1] - pivot_point[1])
            # Get the radius and angle of the point
            r = math.sqrt(rel_pos[0]**2 + rel_pos[1]**2)
            curr_angle = math.atan2(rel_pos[1], rel_pos[0]) / math.pi * 180
            # Get the current angle
            phi = lambda t: curr_angle + degrees * (t - start_time)/(end_time - start_time)
            # Get the position
            return (pivot_point[0] + r * math.cos(phi(t)/180*math.pi),
                    pivot_point[1] + r * math.sin((1 if clockwise else -1) * phi(t)/180*math.pi))
        self.set(start_time, end_time, lambda t: f(t), stay=stay)

        # if start_pos == None:
        #     now = self.time_func(start_time)
        # else:
        #     now = start_pos
        # rel_pos = (now[0] - pivot_point[0], now[1] - pivot_point[1])
        # # Get the radius and angle of the point
        # r = math.sqrt(rel_pos[0]**2 + rel_pos[1]**2)
        # curr_angle = math.atan2(rel_pos[1], rel_pos[0]) / math.pi * 180
        # # Get the current angle
        # phi = lambda t: curr_angle + degrees * (t - start_time)/(end_time - start_time)
        # # Get the position
        # self.set(start_time, end_time, lambda t: (
        #     pivot_point[0] + r * math.cos(phi(t)/180*math.pi),
        #     pivot_point[1] + r * math.sin((1 if clockwise else -1) * phi(t)/180*math.pi),
        # ), stay=stay)
        self.last_change = end_time

    def move_to(self, start_time, end_time, end_pos, stay=True, easing=easings.smooth):
        """Animate the object going from start_pos to end_pos, exponentially"""
        start_pos = self.time_func(start_time)
        dx, dy = start_pos[0]-end_pos[0], start_pos[1]-end_pos[1]

        s, e = start_time, end_time
        self.set(s, e, lambda t: (
            dx * (1-easing((t-s)/(e-s))) + end_pos[0],
            dy * (1-easing((t-s)/(e-s))) + end_pos[1],
        ), stay=stay)
        self.last_change = max(self.last_change, end_time)

    def add(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Set this attribute to func_inner(x)+previous on [start, end]
        lincl, rincl are if the brackets are [/] or (/)"""
        func_outer = self.time_func
        def new_func(t):
            if t < start: return func_outer(t)
            elif t > end:
                if stay: return new_func(end)
                else: return func_outer(t)
            elif not lincl and t == start: return func_outer(t)
            elif not rincl and t == end: return func_outer(t)
            else: return (float(func_outer(t)[0]) + func_inner(t)[0], float(func_outer(t)[1]) + func_inner(t)[1])
        self.time_func = new_func
        self.last_change = max(self.last_change, end_time)


class String(Real):
    """The real attribute is a real-valued attribute (changing) through time"""
    def __init__(self, creation, start_val=''):
        if isinstance(start_val, String):
            self.set_to(start_val)
        else:
            # Define the function
            self.time_func = lambda t: heaviside(creation)(t) * start_val
            # Define the last change time of this attribute (after that it's constant)
            self.last_change = creation


# :::MARKER: Optimisation is only done below


class Color:
    """Parses any input to a workable color internally
    input can be a LinearGradient, RadialGradient, rgb, rgba, name or hex value
    Can return the svg-specifyer for the color"""
    def __init__(self, creation=0, start_color='#000', use=None):
        assert isinstance(creation, int | float)
        if use != None:
            assert isinstance(use, str)
            self.use = use
        if isinstance(start_color, Color):
            self.set_to(start_color)
        else:
            self.use, col = self.parse(start_color)
            if self.use == 'rgb':
                # Define the function
                self.time_func = lambda t: (
                        heaviside(creation)(t) * col[0],
                        heaviside(creation)(t) * col[1],
                        heaviside(creation)(t) * col[2],
                    )
            elif self.use == 'rgba':
                # Define the function
                self.time_func = lambda t: (
                        heaviside(creation)(t) * col[0],
                        heaviside(creation)(t) * col[1],
                        heaviside(creation)(t) * col[2],
                        heaviside(creation)(t) * col[3],
                    )
            else:
                raise NotImplementedError('use has not implemented a time function (yet)')
        self.last_change = creation

    def set(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Set this attribute to func_inner(x) on [start, end]
        lincl, rincl are if the brackets are [/] or (/)"""
        # NOTE: TODO: make some assertions an the type of functions that this is
        # Do we need to parse the color? -> Yes
        # We assume for now it is rgb
        func_outer = self.time_func
        def new_func(t):
            if t < start: return func_outer(t)
            elif t > end:
                if stay: return new_func(end)
                else: return func_outer(t)
            elif not lincl and t == start: return func_outer(t)
            elif not rincl and t == end: return func_outer(t)
            else: return func_inner(t)
        self.time_func = new_func
        self.last_change = max(self.last_change, end)

    def set_to(self, other):
        """Set the value of self to always be the value of other"""
        assert isinstance(other, Color)
        self.use = other.use
        # The value needs to update as the time_function updates
        # we thus use a lambda function
        self.time_func = lambda t: other.time_func(t)
        self.last_change = other.last_change

    def parse(self, color):
        """Parses the color into usage and values"""
        if isinstance(color, colors.LinearGradient):
            raise NotImplementedError('NOTE: TODO')
        elif isinstance(color, colors.RadialGradient):
            raise NotImplementedError('NOTE: TODO')
        elif isinstance(color, tuple):
            if len(color) == 3:  # rgb value
                return ('rgb', color)
            elif len(color) == 4:  # rgba value
                return ('rgba', color)
            else:
                raise ValueError('Length of tuple does not match rgb or rgba lengths')
        elif isinstance(color, str):
            if color[0] != '#':
                # Represents a color name
                color = colors.color_from_name(color.upper())
                # Gets the hex value, thus must still be processed

            if color[0] == '#':
                # Indicator for a hex value
                if len(color) == 4:
                    # of the form #fe0
                    return ('rgb', (int(color[1]*2, 16), int(color[2]*2, 16), int(color[3]*2, 16)))
                elif len(color) == 7:
                    # of the form #ffee00
                    return ('rgb', (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)))
                elif len(color) == 9:
                    # of the form #ffee9900
                    return ('rgba', (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), int(color[7:9], 16)))
                else:
                    raise ValueError('Invalid length of hex color specifyer')
        else:
            raise ValueError('Type of color unknown')

    def random_color(self):
        # Get random value from colors
        # Like colors.random_color() or so
        raise NotImplementedError()

    def at_time(self, time, rounding_func=round):
        """Returns the svg-specifyer for this color"""
        if self.use == 'rgb':
            r, g, b = self.time_func(time)
            r, g, b = rounding_func(r), rounding_func(g), rounding_func(b)
            return f'rgb({r},{g},{b})'
        elif self.use == 'rgba':
            r, g, b, a = self.time_func(time)
            r, g, b, a = rounding_func(r), rounding_func(g), rounding_func(b), rounding_func(a)
            return f'rgba({r},{g},{b},{a})'
        else:
            raise NotImplementedError('use not implemented')

    def interpolate(self, other, start, end, easing=easings.linear):
        """Interpolate this value from start to end with easing to the other value
        Return a lambda function (or this same attribute) for these times"""
        assert self.__class__ == Color  # Both classes need to be a real object
        assert other.__class__ == Color
        if self.use == other.use == 'rgb':
            start_val = self.time_func(start)
            end_val = other.time_func(end)
            # We need to get from start_val to end_val with easing
            new = Color(use='rgb')
            new.time_func = lambda t: tuple(s + (e-s) * easing((t-start)/(end-start)) for s, e in zip(start_val, end_val))
            new.last_change = end
            return new
        else:
            raise NotImplementedError('Only rgb colors can be transformed yet.')


    def set_onward(self, start, value, lincl=True):
        """Set this attribute to value on [start, infty]
        lincl are if the bracket is [/] or (/)"""
        # NOTE: TODO: allowed value to be callable
        use, color = self.parse(value)
        assert use == self.use == 'rgb'  # NOTE: TODO: others
        func_left = self.time_func
        def new_func(t):
            if t < start: return func_left(t)
            elif not lincl and t == start: return func_left(t)
            else: return color
        self.time_func = new_func
        self.last_change = max(self.last_change, start)
