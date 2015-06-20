from django.db import models

class OAuth_Session(models.Model):
    access_key = models.CharField(max_length=50)
    access_secret = models.CharField(max_length=50)
    company_id = models.CharField(max_length=50)

