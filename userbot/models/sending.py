from django.db import models
from django_celery_beat.models import PeriodicTask


class Sending(models.Model):
    id = models.BigIntegerField(primary_key=True)
    topic_id = models.BigIntegerField(null=True, default=None)

    message = models.ForeignKey('Message', on_delete=models.CASCADE)

    schedule = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE)
