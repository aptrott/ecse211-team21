"""
Module for list-like filters that generate statistics based on a source list. 
Changes to the source list result in changes in the filters' results.

Author: Ryan Au
"""

import math
from statistics import mean, median


def range_limit(value: float, lower: float, upper: float) -> float:
    """Prevents the value from going beyond the upper or lower values.

    Example:
    range_limit(40,30,50)->40 (within bounds)
    range_limit(60,30,50)->50 (upper limit)
    range_limit(20,30,50)->30 (lower limit)
    """
    return min(max(value, lower), upper)


def _wrap_index(i, l):
    """Changes an index from negative to the wrapped index based on length l."""
    if i < 0:
        return l + i
    else:
        return i


class AppendingList(object):
    def __init__(self, source: list = None):
        if source is None:
            self.src = []
        else:
            self.src = source

    def __getitem__(self, key):
        return self.src.__getitem__(key)

    def __repr__(self):
        return self.src.__repr__()

    def __contains__(self, key):
        return self.src.__contains__(key)

    def __iter__(self):
        return self.src.__iter__()

    def __len__(self):
        return self.src.__len__()

    def append(self, value):
        return self.src.append(value)


class BaseFilter(AppendingList):
    def __init__(self, source):
        super().__init__(source)

    def __getitem__(self, key):
        if type(key) == int:
            l = len(self.src)
            key = _wrap_index(key, l)
            return self._get_by_key_(key, l)
        if type(key) == slice:
            start, stop, step = key.start, key.stop, key.step
            if start is None:
                start = 0
            if step is None:
                step = 1
            l = len(self.src)
            start = _wrap_index(start, l)
            stop = _wrap_index(stop, l)
            return self._get_by_slice_(start, stop, step, l)

    def _get_by_key_(self, key, l):
        return self.src.__getitem__(key)

    def _get_by_slice_(self, start, stop, step, l):
        return self.src.__getitem__(slice(start, stop, step))

    def __repr__(self):
        return self[:len(self.src)].__repr__()

    def __iter__(self):
        return self[:len(self.src)].__iter__()

    def __contains__(self, key):
        return None


class SimpleFunctionFilter(BaseFilter):
    def __init__(self, source, func):
        super().__init__(source)
        self.func = func

    def _get_by_key_(self, key, l):
        return self.func(super()._get_by_key_(key, l))

    def _get_by_slice_(self, start, stop, step, l):
        return list(map(self.func, super()._get_by_slice_(start, stop, step, l)))


class SectionFunctionFilter(BaseFilter):
    def __init__(self, source, N, func):
        super().__init__(source)
        self.N = N
        self.func = func

    def _get_by_key_(self, key: int, length: int):
        section = int(key // self.N * self.N)
        return self.func(self.src[section:section+self.N])

    def _get_by_slice_(self, start, stop, step, l):
        sstart = start // self.N
        sstop = stop // self.N
        m = [self.func(self.src[i*self.N: i*self.N+self.N])
             for i in range(sstart, sstop+1)]
        return [m[i//self.N] for i in range(start, stop, step)]


class WidthFunctionFilter(BaseFilter):
    def __init__(self, source, width, func):
        super().__init__(source)
        self.width = width
        self.func = func

    def _get_by_key_(self, key: int, length: int):
        index = range_limit(key, 0, length - self.width)
        return self.func(self.src[index:index+self.width])

    def _get_by_slice_(self, start, stop, step, l):
        return [self._get_by_key_(i, len(self.src)) for i in range(start, stop, step)]

    def __len__(self):
        return self.src - self.width

class RangeLimitFilter(SimpleFunctionFilter):
    def __init__(self, source, lower, upper):
        super().__init__(source, lambda x: range_limit(x, lower, upper))


class ModulusFilter(SimpleFunctionFilter):
    def __init__(self, source, mod):
        super().__init__(source, lambda x: x % mod)


class MaximumFilter(WidthFunctionFilter):
    def __init__(self, source, N):
        super().__init__(source, N, max)


class MinimumFilter(WidthFunctionFilter):
    def __init__(self, source, N):
        super().__init__(source, N, min)


class MeanFilter(WidthFunctionFilter):
    def __init__(self, source, N):
        super().__init__(source, N, mean)


class MedianFilter(WidthFunctionFilter):
    def __init__(self, source, N):
        super().__init__(source, N, median)


class SumFilter(WidthFunctionFilter):
    def __init__(self, source, N):
        super().__init__(source, N, sum)


class IntegrationTracker(AppendingList):
    """IntegrationTracker is a special type of list which finds the trapezoidal integral of added values.

    For Example:
    tracker = IntegrationTracker() # instantiate tracker
    tracker.append(0,1) # append with values (y-value, delta-x)
    tracker.append(1)   # same as .append(1,1)
    tracker.append(2,1)   
    tracker.append(3,1)

    print(tracker.get_original()) # gives list of added values (y,dx)
    print(tracker)     # gives integrated values: [0, 0.5, 2, 4.5]
    print(tracker[-1]) # gives 4.5, last added value
    tracker[2] = 3     # will not work, only append or extend can change tracker

    tracker += [0,1,2,3] # appends each element of list
    tracker.extend([0,1,2,3]) # appends each element of list

    tracker += [(0,2), (0,3)] # appends each pair from list as y and dx to tracker
    tracker.extend([(0,2), (0,3)]) # appends each pair from list as y and dx to tracker
    """

    def __init__(self):
        super().__init__()
        self._result = 0
        self._last = 0
        self._original = []

    def append(self, value, dx=1):
        if type(value) != float and type(value) != int:
            raise ValueError(
                "Parameter 'value' must be an acceptable numerical value, float or int")
        if type(dx) != float and type(dx) != int:
            raise ValueError(
                "Parameter 'dx' must be an acceptable numerical value, float or int")

        self._original.append((value, dx))
        if len(self) > 0:
            self._result += (self._last + value) * dx * 0.5
        self._last = value
        super().append(self._result)

    def extend(self, ls):
        self.__iadd__(ls)

    def __iadd__(self, ls):
        ls = list(ls)
        for o in ls:
            try:
                i = iter(o)
                if len(i) > 1:
                    self.append(i[0], i[1])
                else:
                    self.append(i[0])
            except TypeError:
                self.append(o)
        return self

    def reset(self, value=0):
        self._result = value
        self._last = 0

    def get_original(self):
        return tuple(self._original)


def integration(samples: list, delta_time=1):
    """Returns the trapezoidal integration of the samples, given a constant sample time interval.

    Example:
    samples = [0,1,2,3,4] and delta_time=1
    result => [0, 0.5, 2, 4.5, 8]
    (Equivalent of f(x)=x integrated to g(x)=x^2/2)

    delta_time can be a float or a list of floats (the list must be length N-1 as samples N)
    """
    if type(delta_time) == list:
        if not all([type(d) == float or type(d) == int for d in delta_time]):
            return None
        if len(delta_time) != len(samples)-1:
            return None
    elif type(delta_time) == int or type(delta_time) == float:
        m = float(delta_time)
        delta_time = [m for m in range(len(samples)-1)]
    else:
        return None

    N = len(samples)
    result = 0
    ls = [0]
    for i in range(N-1):
        j = i + 1
        result += (samples[i] + samples[j]) * delta_time[i] * 0.5
        ls.append(result)
    return ls


if __name__ == '__main__':
    ls = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    f = MaximumFilter(ls, 2)
    print(f, f[2])
    f = RangeLimitFilter(ls, 1, 7)
    print(f, f[2])
    tracker = IntegrationTracker()
    tracker.append(0)
    tracker.append(1, 1)
    tracker.append(2, 1)
    tracker.append(3, 1)
    tracker.reset()
    tracker.append(0)
    tracker.append(1, 1)
    tracker.append(2, 1)
    tracker.append(3, 1)
    print(tracker)
    tracker.reset()
    tracker += tracker
    print(tracker)
