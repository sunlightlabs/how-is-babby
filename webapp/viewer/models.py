from django.db import models

class Alert(models.Model):
    event_type = models.CharField(max_length=6, null=False, blank=False)

