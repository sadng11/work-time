from django.db import models
from django_jalali.db import models as jmodels
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    objects = jmodels.jManager()
    created_at = jmodels.jDateTimeField(_('Created at'), auto_now_add=True)
    deleted_at = jmodels.jDateTimeField(_('Deleted at'), default=None, null=True)

    class Meta:
        abstract = True
