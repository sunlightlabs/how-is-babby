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
ZEROS = numpy.zeros((480, 640), numpy.uint8)


class Watcher(object):


    def __init__(self):
        self.dsum_buffer = RingBuffer(RING_SIZE)
        self.running_avg = AvgMatrix(FRAME_WINDOW)
        self.frame_count = 0
        self.motion_frames = 0
        self.mode = 'uncalibrated'
        self._set_led = freenect.LED_BLINK_YELLOW


    def set_mode(self, dev, mode):
        if mode == 'nomotion':
            self._set_led = freenect.LED_GREEN
        elif mode == 'motion':
            self._set_led = freenect.LED_RED
        else:
            raise ValueError('unknown mode')
        self.mode = mode


    def depth_callback(self, dev, data, timestamp):
        # add the data to our running average
        self.running_avg.add(data)

        print self.mode, self.frame_count

        if self.mode == 'uncalibrated':
            self.frame_count += 1
            if self.frame_count > 1.5*RING_SIZE:
                self.mode = 'nomotion'
        else:
            mean_array = self.running_avg.mean()
            #diff_array = abs(mean_array.astype(numpy.int16)-data.astype(numpy.int16))
            #diff_array = numpy.where(diff_array/mean_array > PERCENT_THRESHOLD,
            #                         mean_array, ZEROS)

            # difference from sum of buffer
            dsum = mean_array.sum()
            self.dsum_buffer.add(dsum)
            delta = self.dsum_buffer.std_delta(dsum)
            if delta > CHANGE_THRESHOLD:
                self.motion_frames += 1
                if self.motion_frames == MIN_REPORT_EVENT:
                    self.set_mode(dev, 'motion')
            else:
                if self.motion_frames == 1 and self.mode == 'motion':
                    self.set_mode(dev, 'nomotion')
                self.motion_frames = max(self.motion_frames-1, 0)

            cv.ShowImage('DepthAvg', simplify_cv(mean_array.astype(numpy.uint16)))

        # always do this or it freezes
        if cv.WaitKey(10) == 27:
            quit = True

    def body_callback(self, dev, ctx):
        if self._set_led:
            freenect.set_led(dev, self._set_led)
            self._set_led = None


if __name__ == '__main__':
    cv.NamedWindow('DepthAvg')
    watcher = Watcher()
    freenect.runloop(depth=watcher.depth_callback,
                     body=watcher.body_callback)
