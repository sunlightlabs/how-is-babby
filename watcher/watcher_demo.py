#!/usr/bin/env python
import freenect
import cv
import numpy
from utils import RingBuffer, AvgMatrix, simplify_cv

from django.core.management import setup_environ
from webapp import settings
setup_environ(settings)
from webapp.viewer.models import Alert

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


    def set_mode(self, mode):
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

        if self.mode == 'uncalibrated':
            self.frame_count += 1
            if self.frame_count > RING_SIZE:
                self.set_mode('nomotion')
        else:
            mean_array = self.running_avg.mean()
            # diff array not needed unless we want to show where motion is
            #diff_array = abs(mean_array.astype(numpy.int16)-data.astype(numpy.int16))
            #diff_array = numpy.where(diff_array/mean_array > PERCENT_THRESHOLD,
            #                         mean_array, ZEROS)

            # difference from sum of buffer
            dsum = mean_array.sum()
            self.dsum_buffer.add(dsum)
            delta = self.dsum_buffer.std_delta(dsum)

            # frame will count as a motion frame
            if delta > CHANGE_THRESHOLD:
                self.motion_frames += 1
                if (self.motion_frames == MIN_REPORT_EVENT and
                    self.mode == 'nomotion'):
                    self.set_mode('motion')
                    Alert.objects.create(event_type='motion')
            else:
                # don't let motion_frames drop below 0
                self.motion_frames = max(self.motion_frames-1, 0)
                if self.motion_frames == 0 and self.mode == 'motion':
                    self.set_mode('nomotion')
                    # could log how long the event was and its intensity here

            cv.ShowImage('DepthAvg', simplify_cv(mean_array.astype(numpy.uint16)))

        # always do this or it freezes
        cv.WaitKey(1)


    def body_callback(self, dev, ctx):
        # _set_led hackery is required because for some reason calling set_led
        # from update loop hangs the process
        if self._set_led:
            freenect.set_led(dev, self._set_led)
            self._set_led = None


if __name__ == '__main__':
    cv.NamedWindow('DepthAvg')
    watcher = Watcher()
    freenect.runloop(depth=watcher.depth_callback,
                     body=watcher.body_callback)
