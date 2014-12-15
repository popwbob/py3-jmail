from django.db import models

class JMailUser(models.Model):
    email = models.EmailField(max_length=254, unique=True)
