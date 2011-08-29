#!/usr/bin/env python
import freenect
import cv
import numpy
from utils import RingBuffer, AvgMatrix, simplify_cv

# globals
PERCENT_THRESHOLD = 0.1
FRAME_WINDOW = 30
dsum_buffer = RingBuffer(1000)
ZEROS = numpy.zeros((480, 640), numpy.uint8)
running_avg = AvgMatrix(FRAME_WINDOW)


def depth_callback(dev, data, timestamp):
    global dsum_buffer
    global running_avg

    running_avg.add(data)
    mean_array = running_avg.mean()
    diff_array = abs(mean_array.astype(numpy.int16)-data.astype(numpy.int16))

    diff_array = numpy.where(diff_array/mean_array > PERCENT_THRESHOLD,
                             mean_array, ZEROS)

    # difference from sum of buffer
    #dsum = diff_array.sum()
    #dsum_buffer.add(dsum)
    #delta = dsum_buffer.std_delta(dsum)
    #if delta > 0.5:
    #    print 'dsum motion', delta

    img = simplify_cv(data.copy())
    #cv.ShowImage('Depth', img)
    cv.ShowImage('DepthAvg', simplify_cv(mean_array.astype(numpy.uint16)))
    cv.ShowImage('DepthDiff', simplify_cv(diff_array.astype(numpy.uint16)))
    if cv.WaitKey(10) == 27:
        raise Exception('quit!')


if __name__ == '__main__':
    #cv.NamedWindow('Depth')
    cv.NamedWindow('DepthAvg')
    cv.NamedWindow('DepthDiff')
    freenect.runloop(depth=depth_callback)
