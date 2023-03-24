"""
NOTE: these easings/rate functions are copied from
https://github.com/ManimCommunity/manim/blob/main/manim/utils/rate_functions.py

MIT License

Copyright (c) 2018 3Blue1Brown LLC
Copyright (c) 2021, the Manim Community Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import typing
from functools import wraps
import numpy as np


# This is a decorator that makes sure any function it's used on will
# return 0 if t<0 and 1 if t>1.
def unit_interval(function):
    @wraps(function)
    def wrapper(t, *args, **kwargs):
        if 0 <= t <= 1:
            return function(t, *args, **kwargs)
        elif t < 0:
            return 0
        else:
            return 1

    return wrapper


# This is a decorator that makes sure any function it's used on will
# return 0 if t<0 or t>1.
def zero(function):
    @wraps(function)
    def wrapper(t, *args, **kwargs):
        if 0 <= t <= 1:
            return function(t, *args, **kwargs)
        else:
            return 0

    return wrapper

def sigmoid(x: float) -> float:
    r"""Returns the output of the logistic function.
    The logistic function, a common example of a sigmoid function, is defined
    as :math:`\frac{1}{1 + e^{-x}}`.
    References
    ----------
    - https://en.wikipedia.org/wiki/Sigmoid_function
    - https://en.wikipedia.org/wiki/Logistic_function
    """
    return 1.0 / (1 + np.exp(-x))

@unit_interval
def linear(t: float) -> float:
    return t


@unit_interval
def smooth(t: float, inflection: float = 10.0) -> float:
    error = sigmoid(-inflection / 2)
    return min(
        max((sigmoid(inflection * (t - 0.5)) - error) / (1 - 2 * error), 0),
        1,
    )


@unit_interval
def rush_into(t: float, inflection: float = 10.0) -> float:
    return 2 * smooth(t / 2.0, inflection)


@unit_interval
def rush_from(t: float, inflection: float = 10.0) -> float:
    return 2 * smooth(t / 2.0 + 0.5, inflection) - 1


@unit_interval
def slow_into(t: float) -> float:
    return np.sqrt(1 - (1 - t) * (1 - t))


@unit_interval
def double_smooth(t: float) -> float:
    if t < 0.5:
        return 0.5 * smooth(2 * t)
    else:
        return 0.5 * (1 + smooth(2 * t - 1))


@zero
def there_and_back(t: float, inflection: float = 10.0) -> float:
    new_t = 2 * t if t < 0.5 else 2 * (1 - t)
    return smooth(new_t, inflection)


@zero
def there_and_back_with_pause(t: float, pause_ratio: float = 1.0 / 3) -> float:
    a = 1.0 / pause_ratio
    if t < 0.5 - pause_ratio / 2:
        return smooth(a * t)
    elif t < 0.5 + pause_ratio / 2:
        return 1
    else:
        return smooth(a - a * t)

def not_quite_there(
    func: typing.Callable[[float], float] = smooth,
    proportion: float = 0.7,
) -> typing.Callable[[float], float]:
    def result(t):
        return proportion * func(t)

    return result


@zero
def wiggle(t: float, wiggles: float = 2) -> float:
    return there_and_back(t) * np.sin(wiggles * np.pi * t)


def squish_rate_func(
    func: typing.Callable[[float], float],
    a: float = 0.4,
    b: float = 0.6,
) -> typing.Callable[[float], float]:
    def result(t):
        if a == b:
            return a

        if t < a:
            return func(0)
        elif t > b:
            return func(1)
        else:
            return func((t - a) / (b - a))

    return result


# Stylistically, should this take parameters (with default values)?
# Ultimately, the functionality is entirely subsumed by squish_rate_func,
# but it may be useful to have a nice name for with nice default params for
# "lingering", different from squish_rate_func's default params


@unit_interval
def lingering(t: float) -> float:
    return squish_rate_func(lambda t: t, 0, 0.8)(t)


@unit_interval
def exponential_decay(t: float, half_life: float = 0.1) -> float:
    # The half-life should be rather small to minimize
    # the cut-off error at the end
    return 1 - np.exp(-t / half_life)


@unit_interval
def ease_in_sine(t: float) -> float:
    return 1 - np.cos((t * np.pi) / 2)


@unit_interval
def ease_out_sine(t: float) -> float:
    return np.sin((t * np.pi) / 2)


@unit_interval
def ease_in_out_sine(t: float) -> float:
    return -(np.cos(np.pi * t) - 1) / 2


@unit_interval
def ease_in_quad(t: float) -> float:
    return t * t


@unit_interval
def ease_out_quad(t: float) -> float:
    return 1 - (1 - t) * (1 - t)


@unit_interval
def ease_in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2


@unit_interval
def ease_in_cubic(t: float) -> float:
    return t * t * t


@unit_interval
def ease_out_cubic(t: float) -> float:
    return 1 - pow(1 - t, 3)


@unit_interval
def ease_in_out_cubic(t: float) -> float:
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


@unit_interval
def ease_in_quart(t: float) -> float:
    return t * t * t * t


@unit_interval
def ease_out_quart(t: float) -> float:
    return 1 - pow(1 - t, 4)


@unit_interval
def ease_in_out_quart(t: float) -> float:
    return 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2


@unit_interval
def ease_in_quint(t: float) -> float:
    return t * t * t * t * t


@unit_interval
def ease_out_quint(t: float) -> float:
    return 1 - pow(1 - t, 5)


@unit_interval
def ease_in_out_quint(t: float) -> float:
    return 16 * t * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 5) / 2


@unit_interval
def ease_in_expo(t: float) -> float:
    return 0 if t == 0 else pow(2, 10 * t - 10)


@unit_interval
def ease_out_expo(t: float) -> float:
    return 1 if t == 1 else 1 - pow(2, -10 * t)


@unit_interval
def ease_in_out_expo(t: float) -> float:
    if t == 0:
        return 0
    elif t == 1:
        return 1
    elif t < 0.5:
        return pow(2, 20 * t - 10) / 2
    else:
        return (2 - pow(2, -20 * t + 10)) / 2


@unit_interval
def ease_in_circ(t: float) -> float:
    return 1 - np.sqrt(1 - pow(t, 2))


@unit_interval
def ease_out_circ(t: float) -> float:
    return np.sqrt(1 - pow(t - 1, 2))


@unit_interval
def ease_in_out_circ(t: float) -> float:
    return (
        (1 - np.sqrt(1 - pow(2 * t, 2))) / 2
        if t < 0.5
        else (np.sqrt(1 - pow(-2 * t + 2, 2)) + 1) / 2
    )


@unit_interval
def ease_in_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t


@unit_interval
def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


@unit_interval
def ease_in_out_back(t: float) -> float:
    c1 = 1.70158
    c2 = c1 * 1.525
    return (
        (pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
        if t < 0.5
        else (pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
    )


@unit_interval
def ease_in_elastic(t: float) -> float:
    c4 = (2 * np.pi) / 3
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        return -pow(2, 10 * t - 10) * np.sin((t * 10 - 10.75) * c4)


@unit_interval
def ease_out_elastic(t: float) -> float:
    c4 = (2 * np.pi) / 3
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        return pow(2, -10 * t) * np.sin((t * 10 - 0.75) * c4) + 1


@unit_interval
def ease_in_out_elastic(t: float) -> float:
    c5 = (2 * np.pi) / 4.5
    if t == 0:
        return 0
    elif t == 1:
        return 1
    elif t < 0.5:
        return -(pow(2, 20 * t - 10) * np.sin((20 * t - 11.125) * c5)) / 2
    else:
        return (pow(2, -20 * t + 10) * np.sin((20 * t - 11.125) * c5)) / 2 + 1


@unit_interval
def ease_in_bounce(t: float) -> float:
    return 1 - ease_out_bounce(1 - t)


@unit_interval
def ease_out_bounce(t: float) -> float:
    n1 = 7.5625
    d1 = 2.75

    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        return n1 * (t - 1.5 / d1) * (t - 1.5 / d1) + 0.75
    elif t < 2.5 / d1:
        return n1 * (t - 2.25 / d1) * (t - 2.25 / d1) + 0.9375
    else:
        return n1 * (t - 2.625 / d1) * (t - 2.625 / d1) + 0.984375


@unit_interval
def ease_in_out_bounce(t: float) -> float:
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    else:
        return (1 + ease_out_bounce(2 * t - 1)) / 2
