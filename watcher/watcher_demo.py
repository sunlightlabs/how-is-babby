#!/usr/bin/env python
import freenect
import cv
import numpy
from utils import RingBuffer, AvgMatrix, simplify_cv

# globals
dsum_buffer = RingBuffer(1000)
running_avg = AvgMatrix(15)
ZEROS = numpy.zeros((480,640), numpy.uint8)


def depth_callback(dev, data, timestamp):
    global dsum_buffer
    global running_avg

    running_avg.add(data)
    mean_array = running_avg.mean()

    # difference from sum of buffer
    dsum = mean_array.sum()
    dsum_buffer.add(dsum)
    delta = dsum_buffer.std_delta(dsum)
    if delta > 0.5:
        print 'dsum motion', delta

    img = simplify_cv(data.copy())
    cv.ShowImage('Depth', img)
    cv.ShowImage('DepthDiff', simplify_cv(mean_array.astype(numpy.uint16)))
    if cv.WaitKey(10) == 27:
        raise Exception('quit!')

if __name__ == '__main__':
    cv.NamedWindow('Depth')
    cv.NamedWindow('DepthDiff')
    freenect.runloop(depth=depth_callback)

