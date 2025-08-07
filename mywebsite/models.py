# mywebsite/models.py

from django.db import models

class QueueConfig(models.Model):
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    queue_name = models.CharField(max_length=100)
    target = models.GenericIPAddressField()
    max_limit = models.CharField(max_length=50)  # contoh: "2M/2M"

    def __str__(self):
        return self.queue_name
