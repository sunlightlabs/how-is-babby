#!/usr/bin/env python
import freenect
import frame_convert
import cv
import numpy
from pylab import ion, plot, draw, axis, imshow
import time

depth_acc = cv.fromarray(numpy.zeros((480,640), dtype=numpy.float32))

cv.NamedWindow('Depth')

class RingBuffer(object):

    def __init__(self, size):
        self._size = size
        self._buffer = [0]*size

    def add(self, value):
        self._buffer.append(value)
        self._buffer = self._buffer[-self._size:]

    def mean(self):
        return numpy.mean(self._buffer)

    def stddev(self):
        return numpy.std(self._buffer)

    def delta(self, val):
        return abs(self.mean()-val)

    def std_delta(self, val):
        return float(self.delta(val))/self.stddev()


dsum_buffer = RingBuffer(100)

def simplify_cv(data):
    img = frame_convert.pretty_depth_cv(data)
    return img

def depth_callback(dev, data, timestamp):
    global dsum_buffer

    # use runningAvg
    cv.RunningAvg(cv.fromarray(data.astype(numpy.float32)),
                  depth_acc, 0.01)
    depth_diff = depth_acc - data

    # difference from sum of buffer
    dsum = data.sum()
    dsum_buffer.add(dsum)
    delta = dsum_buffer.std_delta(dsum)
    if delta > 2.0:
        print 'motion!', delta

    img = simplify_cv(data)
    cv.ShowImage('Depth', img)
    if cv.WaitKey(10) == 27:
        raise Exception('quit!')

freenect.runloop(depth=depth_callback)
