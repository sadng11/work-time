from django import forms
from django.forms.widgets import DateTimeBaseInput
from django.utils.translation import gettext_lazy as _

from .models import Project, TimeEntry


class JDateTimeInput(DateTimeBaseInput):
    format_key = "DATETIME_INPUT_FORMATS"
    template_name = "django/forms/widgets/datetime.html"

    def format_value(self, value):
        if value:
            if hasattr(value, 'strftime'):
                return value.strftime('%Y-%m-%d %H:%M')
            val_str = str(value)
            if '.' in val_str:
                val_str = val_str.split('.')[0]
            return val_str
        return ''


class TimeEntryForm(forms.ModelForm):
    """فرم ثبت سریع زمان ورود/خروج بر اساس پروژه"""
    class Meta:
        model = TimeEntry
        fields = ['project', 'entry_time', 'description']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'entry_time': JDateTimeInput(attrs={'class': 'form-control', 'data-jdp': True, 'autocomplete': 'off'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('توضیحات اختیاری...')}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['project'].queryset = Project.objects.filter(user=user)


class ManualTimeEntryForm(forms.ModelForm):
    """فرم ثبت دستی و ویرایش سوابق کاری گذشته با زمان ورود و خروج مشخص"""
    class Meta:
        model = TimeEntry
        fields = ['project', 'entry_time', 'exit_time', 'description']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'entry_time': JDateTimeInput(attrs={'class': 'form-control', 'data-jdp': True, 'autocomplete': 'off'}),
            'exit_time': JDateTimeInput(attrs={'class': 'form-control', 'data-jdp': True, 'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('توضیحات کار انجام‌شده...')}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['project'].queryset = Project.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        entry_time = cleaned_data.get('entry_time')
        exit_time = cleaned_data.get('exit_time')

        if entry_time and exit_time and exit_time <= entry_time:
            raise forms.ValidationError(_("زمان خروج باید بعد از زمان شروع (ورود) باشد."))

        return cleaned_data