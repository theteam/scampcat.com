from django.db import models

from django_extensions.db.fields import (CreationDateTimeField,
                                         ModificationDateTimeField)

class TimestampAbstract(models.Model):
    """
    Subclass this to get timestamp fields.
    """
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    class Meta:
        abstract = True
