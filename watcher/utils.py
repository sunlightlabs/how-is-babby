import numpy
import frame_convert

def simplify_cv(data):
    img = frame_convert.pretty_depth_cv(data)
    return img


class RingBuffer(object):

    def __init__(self, size):
        self._size = size
        self._buffer = [0]*size

    def add(self, value):
        self._buffer.append(value)
        self._buffer.pop(0)

    def mean(self):
        return numpy.mean(self._buffer)

    def stddev(self):
        return numpy.std(self._buffer)

    def delta(self, val):
        return abs(self.mean()-val)

    def std_delta(self, val):
        return float(self.delta(val))/self.stddev()


class AvgMatrix(RingBuffer):

    def __init__(self, size):
        self._size = size
        self._buffer = []
        for i in xrange(size):
            self._buffer.append(numpy.zeros((480,640), dtype=numpy.float32))
        assert len(self._buffer) == size

    def mean(self):
        assert len(self._buffer) == self._size
        return sum(self._buffer)/self._size
