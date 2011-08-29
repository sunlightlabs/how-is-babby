#!/usr/bin/env python
import freenect
import cv
import numpy
from utils import RingBuffer, AvgMatrix, simplify_cv

# globals
PERCENT_THRESHOLD = 0.0
FRAME_WINDOW = 15
CHANGE_THRESHOLD = 1.1
RING_SIZE = 100
MIN_REPORT_EVENT = 20

dsum_buffer = RingBuffer(RING_SIZE)
ZEROS = numpy.zeros((480, 640), numpy.uint8)
running_avg = AvgMatrix(FRAME_WINDOW)

frames = 0
calibrated = False
motion_frames = 0

def depth_callback(dev, data, timestamp):
    global dsum_buffer
    global running_avg
    global calibrated
    global frames
    global motion_began
    global motion_frames

    frames += 1
    if frames > 1.5*RING_SIZE and not calibrated:
        print 'Calibrated!'
        calibrated = True

    running_avg.add(data)

    if calibrated:
        mean_array = running_avg.mean()
        diff_array = abs(mean_array.astype(numpy.int16)-data.astype(numpy.int16))
        diff_array = numpy.where(diff_array/mean_array > PERCENT_THRESHOLD,
                                 mean_array, ZEROS)

        # difference from sum of buffer
        dsum = mean_array.sum()
        dsum_buffer.add(dsum)
        delta = dsum_buffer.std_delta(dsum)
        if delta > CHANGE_THRESHOLD:
            motion_began = timestamp
            motion_frames += 1

            if motion_frames == MIN_REPORT_EVENT:
                print 'motion event...',
        else:
            if motion_frames == 1:
                print 'ended'
            motion_frames = max(motion_frames-1, 0)

        cv.ShowImage('DepthAvg', simplify_cv(mean_array.astype(numpy.uint16)))
        cv.ShowImage('DepthDiff', simplify_cv(diff_array.astype(numpy.uint16)))
        if cv.WaitKey(10) == 27:
            raise Exception('quit!')


if __name__ == '__main__':
    #cv.NamedWindow('Depth')
    cv.NamedWindow('DepthAvg')
    cv.NamedWindow('DepthDiff')
    freenect.runloop(depth=depth_callback)
