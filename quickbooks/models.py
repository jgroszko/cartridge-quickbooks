from django.db import models

class OAuth_Session(models.Model):
    access_token = models.CharField(max_length=1024, null=True)
    refresh_token = models.CharField(max_length=50, null=True)

    company_id = models.CharField(max_length=50)

    updated = models.DateTimeField(auto_now=True)
