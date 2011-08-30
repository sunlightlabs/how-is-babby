from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    event_type = models.CharField(max_length=6, null=False, blank=False)
    # we'll also need a timestamp for queueing events

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    motion_sensitivity = models.IntegerField()
    #TODO:
    #sound_sensitivity = models.IntegerField()

    distance = models.IntegerField()

    sms_email = models.EmailField()
    sms_on = models.BooleanField()

    nightvision_on = models.BooleanField()




