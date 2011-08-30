from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms


class Alert(models.Model):
    event_type = models.CharField(max_length=6, null=False, blank=False)
    timestamp = models.DateTimeField()
    # we'll also need a timestamp for queueing events


MOTION_SENSITIVITY_CHOICES = ((5, 'Low'),(10, 'Medium'),(20, 'High'))


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    motion_sensitivity = models.IntegerField(choices=MOTION_SENSITIVITY_CHOICES, null=False, blank=False, default=10)
    #TODO:
    #sound_sensitivity = models.IntegerField()

    distance = models.IntegerField(null=False, blank=False, default=10)

    sms_email = models.EmailField()
    sms_on = models.BooleanField(null=False, default=False)

    nightvision_on = models.BooleanField(null=False, default=False)


class ConfigForm(ModelForm):
    user = forms.IntegerField(widget=forms.HiddenInput())
    class Meta:
        model = UserProfile



