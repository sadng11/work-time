from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels
from work_time.model import BaseModel


class Project(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Project name"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    employer = models.CharField(max_length=100, verbose_name=_("Employer"), null=True, blank=True, default=None)
    unit_price = models.BigIntegerField(verbose_name=_("Unit price"), default=None, null=True, blank=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")


class TimeEntry(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_("Project"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    entry_time = jmodels.jDateTimeField(verbose_name=_("Entry time"))
    exit_time = jmodels.jDateTimeField(null=True, blank=True, verbose_name=_("Exit time"))
    duration = models.DurationField(null=True, blank=True, verbose_name=_("Duration"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))

    def save(self, *args, **kwargs):
        if self.entry_time and hasattr(self.entry_time, 'microsecond') and self.entry_time.microsecond:
            self.entry_time = self.entry_time.replace(microsecond=0)
        if self.exit_time and hasattr(self.exit_time, 'microsecond') and self.exit_time.microsecond:
            self.exit_time = self.exit_time.replace(microsecond=0)
        if self.exit_time and self.entry_time:
            self.duration = self.exit_time - self.entry_time
        super().save(*args, **kwargs)

    @property
    def cal_duration(self):
        if self.duration:
            days = self.duration.days
            seconds = self.duration.seconds

            minutes = seconds // 60

            hours = minutes // 60
            minutes = minutes % 60
            dur_string = f'{hours}  ساعت {minutes:02d}دقیقه '
            if days:
                dur_string = f'{days} روز {dur_string}'
            return dur_string
        return None

    @property
    def fee(self):
        """محاسبه مبلغ کارکرد به تومان بر اساس مدت زمان و نرخ ساعتی پروژه"""
        if self.duration and self.project and self.project.unit_price:
            hours = self.duration.total_seconds() / 3600
            return round(hours * self.project.unit_price)
        return 0

    @property
    def formatted_fee(self):
        """نمایش مبلغ با جداکننده هزارگان به تومان"""
        return f"{self.fee:,}"

    class Meta:
        verbose_name = _("Time Entry")
        verbose_name_plural = _("Time Entries")