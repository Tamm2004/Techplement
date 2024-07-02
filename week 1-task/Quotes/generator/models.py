from django.db import models

# Create your models here.


class quote(models.Model):
    content = models.TextField()
    author = models.CharField(max_length=255)