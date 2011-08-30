#!/usr/bin/env python
import time
import freenect
import boto
import cv
import numpy
from utils import RingBuffer, AvgMatrix, simplify_cv
from frame_convert import video_cv

from django.core.management import setup_environ
from webapp import settings
setup_environ(settings)
from webapp.viewer.models import Alert, UserProfile

class Watcher(object):


    def __init__(self):
        self.frame_count = 0
        self.motion_frames = 0
        self.mode = 'uncalibrated'
        self._set_led = freenect.LED_BLINK_YELLOW
        self._last_img = 0
        self._last_setting_check = 0

        self.settings_delay = 5

        self.debug = True
        self.nightvision = None
        self._set_video = None
        self.dsum_buffer = RingBuffer(100)
        self.running_avg = AvgMatrix(15)
        self.load_settings()

        self.s3bucket = boto.connect_s3(settings.AWS_KEY,
                                        settings.AWS_SECRET).create_bucket(
                                            settings.AWS_BUCKET)

    def load_settings(self):
        profile = UserProfile.objects.get()

        if self.debug:
            print 'load_settings', profile.motion_sensitivity, profile.nightvision_on

        self.snapshot_secs = 5

        # low
        if profile.motion_sensitivity < 10:
            self.change_threshold = 1.5
            self.min_report_event = 30
        # high
        elif profile.motion_sensitivity > 10:
            self.change_threshold = 0.7
            self.min_report_event = 15
        # normal
        else:
            self.change_threshold = 1.0
            self.min_report_event = 20

        self.debug = True
        #self.debug = profile.debug

        if profile.nightvision_on != self.nightvision:
            self.nightvision = profile.nightvision_on
            self._set_video = (freenect.VIDEO_IR_8BIT if self.nightvision
                               else freenect.VIDEO_RGB)


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
            if self.frame_count == self.dsum_buffer.size():
                self.set_mode('nomotion')
        else:
            mean_array = self.running_avg.mean()

            # difference from sum of buffer
            dsum = mean_array.sum()
            self.dsum_buffer.add(dsum)
            delta = self.dsum_buffer.std_delta(dsum)

            # frame will count as a motion frame
            if delta > self.change_threshold:
                self.motion_frames += 1
                if (self.motion_frames == self.min_report_event and
                    self.mode == 'nomotion'):
                    self.set_mode('motion')
                    Alert.objects.create(event_type='motion')
            else:
                # don't let motion_frames drop below 0
                self.motion_frames = max(self.motion_frames-1, 0)
                if self.motion_frames == 0 and self.mode == 'motion':
                    self.set_mode('nomotion')
                    # could log how long the event was and its intensity here

            if self.debug:
                cv.ShowImage('Depth', simplify_cv(mean_array.astype(numpy.uint16)))
                cv.WaitKey(1)


    def body_callback(self, dev, ctx):
        # _set_led hackery is required because for some reason calling set_led
        # from update loop hangs the process
        if self._set_led:
            freenect.set_led(dev, self._set_led)
            self._set_led = None

        if self._set_video is not None:
            freenect.stop_video(dev)
            freenect.set_video_mode(dev, freenect.RESOLUTION_MEDIUM,
                                    self._set_video)
            freenect.start_video(dev)
            self._set_video = None

        if self._last_setting_check + self.settings_delay < time.time():
            self.load_settings()
            self._last_setting_check = time.time()


    def video_callback(self, dev, data, timestamp):
        if self.nightvision:
            cv_data = simplify_cv(data)
        else:
            cv_data = video_cv(data)

        if self.debug:
            cv.ShowImage('Video', cv_data)

        if self._last_img + self.snapshot_secs < time.time():
            cv.SaveImage('babby-current.jpg', cv_data)
            k = boto.s3.key.Key(self.s3bucket)
            k.key = '/babby/current.jpg'
            k.set_contents_from_filename('babby-current.jpg')
            k.set_acl('public-read')
            self._last_img = time.time()


if __name__ == '__main__':
    cv.NamedWindow('Video')
    cv.NamedWindow('Depth')
    watcher = Watcher()
    freenect.runloop(depth=watcher.depth_callback,
                     video=watcher.video_callback,
                     body=watcher.body_callback)
