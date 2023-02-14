from django.db import models

# Create your models here.
from JobPortal.models import AbstractBaseModel


class Locations(AbstractBaseModel):
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    country_code_iso2 = models.CharField(max_length=7)
    country_code_iso3 = models.CharField(max_length=7)
    state = models.CharField(max_length=50)

    class Meta:
        unique_together = ('city', 'country', 'state')
