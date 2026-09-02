from django import forms
from django.forms.widgets import DateTimeBaseInput

from .models import Project, TimeEntry


class JDateTimeInput(DateTimeBaseInput):
    format_key = "DATETIME_INPUT_FORMATS"
    template_name = "django/forms/widgets/datetime.html"

    def format_value(self, value):
        return value


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['project', 'entry_time', 'description']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'entry_time': JDateTimeInput(attrs={'class': 'form-control', 'data-jdp':True, 'autocomplete':'off'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }