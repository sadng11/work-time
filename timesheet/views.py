import random

import jdatetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from jdatetime import timedelta

from .models import Project, TimeEntry
from .forms import TimeEntryForm
from django.db.models import Sum
from num2fawords import words

@login_required
def home(request):
    if request.method == 'POST':
        time_entry_form = TimeEntryForm(request.POST)
        if time_entry_form.is_valid():
            last_entry = TimeEntry.objects.filter(user=request.user,
                                                  project=time_entry_form.instance.project_id).order_by('-id').first()
            if last_entry and not last_entry.exit_time:
                last_entry.exit_time = time_entry_form.cleaned_data['entry_time']
                last_entry.save()
            else:
                time_entry = time_entry_form.save(commit=False)
                time_entry.user = request.user
                time_entry.save()
            return redirect('home')
    else:
        time_entry_form = TimeEntryForm()

    projects = Project.objects.filter(user=request.user)
    time_entries = TimeEntry.objects.filter(user=request.user).order_by('-entry_time')[:10]
    today = jdatetime.date.today()
    start_date = jdatetime.date(today.year, today.month, 1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    return render(request, 'home.html', {
        'time_entry_form': time_entry_form,
        'projects': projects,
        'start_date': start_date,
        'end_date': end_date,
        'time_entries': time_entries,
    })


@login_required
def report(request):
    query_params = request.GET
    time_entries = TimeEntry.objects.filter(user=request.user, exit_time__isnull=False)
    if query_params.get('start') and query_params.get('end'):
        time_entries = time_entries.filter(entry_time__date__gte=query_params.get('start'),
                                           entry_time__date__lte=query_params.get('end'))
    if query_params.get('project_id'):
        time_entries = time_entries.filter(project_id=query_params.get('project_id'))
    daily_report = time_entries.values('entry_time', 'project__name', 'description', 'id').annotate(
        total_duration=Sum('duration')).order_by(
        '-entry_time')

    deltas = []
    for item in daily_report:
        deltas.append(item['total_duration'])
    total_duration = sum(deltas, timedelta())
    change_day_to_hour = 0
    if total_duration.days:
        change_day_to_hour = total_duration.days * 24
    change_second_to_hour = 0
    if total_duration.seconds:
        change_second_to_hour = total_duration.seconds / 3600
    total_hours = change_second_to_hour + change_day_to_hour
    project = None
    if query_params.get('project_id'):
        project = Project.objects.get(id=query_params.get('project_id'))
    project_list = Project.objects.values('id', 'name')
    return render(request, 'report.html', {
        'daily_report': daily_report,
        'total_hours': total_hours,
        "total_duration": total_duration,
        "start": query_params.get('start'),
        "end": query_params.get('end'),
        "project_id": query_params.get('project_id'),
        "project": project,
        "project_list": project_list,
    })


@login_required
def factor(request, start=None, end=None, project=None):
    time_entries = TimeEntry.objects.filter(user=request.user, exit_time__isnull=False)
    if start and end:
        time_entries = time_entries.filter(entry_time__date__gte=start,
                                           entry_time__date__lte=end)
    if project:
        time_entries = time_entries.filter(project_id=project)
    daily_report = time_entries.values('entry_time').annotate(total_duration=Sum('duration')).order_by('-entry_time')
    deltas = []
    for item in daily_report:
        deltas.append(item['total_duration'])
    total_duration = sum(deltas, timedelta())
    change_day_to_hour = 0
    if total_duration.days:
        change_day_to_hour = total_duration.days * 24
    change_second_to_hour = 0
    if total_duration.seconds:
        change_second_to_hour = total_duration.seconds / 3600
    total_hours = round(change_second_to_hour + change_day_to_hour)

    project = Project.objects.get(id=project)
    base_fee = project.unit_price if project.unit_price else 300_000
    total_fee = round(total_hours * base_fee)
    return render(request, 'factor.html', {
        'total_hours': f"{total_hours:,}",
        "base_fee": f"{base_fee:,}",
        "total_fee": f"{total_fee :,}",
        "string_fee":f"{words(total_fee)}",
        "start_date": start,
        "end_date": end,
        "project": project,
        "invoice_number": f"{jdatetime.datetime.now().strftime('%Y%m%d')}/{random.choice([i for i in range(1, 10)])}",
        "today": jdatetime.datetime.now(),
        "user":request.user
    })
