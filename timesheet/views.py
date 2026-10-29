import random

import jdatetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jdatetime import timedelta
from django.db.models import Sum
from num2fawords import words

from .models import Project, TimeEntry
from .forms import TimeEntryForm, ManualTimeEntryForm
from .export import export_daily_report_to_excel
from .analytics import get_analytics_context
import json


@login_required
def home(request):
    action = request.POST.get('action', 'quick_entry') if request.method == 'POST' else None

    if request.method == 'POST':
        if action == 'manual_entry':
            manual_form = ManualTimeEntryForm(request.POST, user=request.user)
            time_entry_form = TimeEntryForm(user=request.user)
            if manual_form.is_valid():
                time_entry = manual_form.save(commit=False)
                time_entry.user = request.user
                time_entry.save()
                messages.success(request, 'رکورد جدید با موفقیت ثبت شد.')
                return redirect('home')
        else:
            time_entry_form = TimeEntryForm(request.POST, user=request.user)
            manual_form = ManualTimeEntryForm(user=request.user)
            if time_entry_form.is_valid():
                last_entry = TimeEntry.objects.filter(
                    user=request.user,
                    project=time_entry_form.instance.project_id
                ).order_by('-id').first()
                if last_entry and not last_entry.exit_time:
                    last_entry.exit_time = time_entry_form.cleaned_data['entry_time']
                    last_entry.save()
                    messages.success(request, f'زمان خروج برای پروژه «{last_entry.project.name}» ثبت شد.')
                else:
                    time_entry = time_entry_form.save(commit=False)
                    time_entry.user = request.user
                    time_entry.save()
                    messages.success(request, f'زمان ورود برای پروژه «{time_entry.project.name}» ثبت شد.')
                return redirect('home')
    else:
        time_entry_form = TimeEntryForm(user=request.user)
        manual_form = ManualTimeEntryForm(user=request.user)

    projects = Project.objects.filter(user=request.user)
    time_entries = TimeEntry.objects.filter(user=request.user).order_by('-entry_time')[:15]
    today = jdatetime.date.today()
    start_date = jdatetime.date(today.year, today.month, 1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    active_timer = TimeEntry.objects.filter(user=request.user, exit_time__isnull=True).order_by('-entry_time').first()
    active_timer_elapsed_seconds = 0
    if active_timer:
        active_timer_elapsed_seconds = max(0, int((jdatetime.datetime.now() - active_timer.entry_time).total_seconds()))

    return render(request, 'home.html', {
        'time_entry_form': time_entry_form,
        'manual_form': manual_form,
        'projects': projects,
        'start_date': start_date,
        'end_date': end_date,
        'time_entries': time_entries,
        'active_timer': active_timer,
        'active_timer_elapsed_seconds': active_timer_elapsed_seconds,
    })


@login_required
def start_timer(request):
    """شروع تایمر زنده برای یک پروژه مشخص (و بستن خودکار تایمر فعال قبلی در صورت وجود)"""
    if request.method == 'POST':
        project_id = request.POST.get('project')
        description = request.POST.get('description', '').strip()

        if not project_id:
            messages.error(request, 'لطفاً ابتدا یک پروژه را برای شروع تایمر انتخاب نمایید.')
            return redirect('home')

        project = get_object_or_404(Project, id=project_id, user=request.user)

        # در صورت وجود تایمر فعال قبلی، آن را هوشمندانه می‌بندیم
        previous_active = TimeEntry.objects.filter(user=request.user, exit_time__isnull=True).first()
        now = jdatetime.datetime.now().replace(microsecond=0)
        if previous_active:
            previous_active.exit_time = now
            previous_active.save()
            messages.info(request, f'تایمر کارکرد قبلی مربوط به پروژه «{previous_active.project.name}» ذخیره شد.')

        # ایجاد تایمر جدید
        new_entry = TimeEntry.objects.create(
            user=request.user,
            project=project,
            entry_time=now,
            description=description,
        )
        messages.success(request, f'تایمر کارکرد برای پروژه «{project.name}» با موفقیت فعال شد.')

    return redirect('home')


@login_required
def stop_timer(request):
    """توقف تایمر فعال و ثبت زمان خروج و محاسبه مدت کارکرد"""
    if request.method == 'POST':
        active = TimeEntry.objects.filter(user=request.user, exit_time__isnull=True).order_by('-entry_time').first()
        if active:
            active.exit_time = jdatetime.datetime.now().replace(microsecond=0)
            new_desc = request.POST.get('description', '').strip()
            if new_desc:
                active.description = new_desc
            active.save()
            dur_msg = active.cal_duration or 'کمتر از یک دقیقه'
            messages.success(request, f'کارکرد پروژه «{active.project.name}» با موفقیت متوقف و ذخیره شد ({dur_msg}).')
        else:
            messages.warning(request, 'در حال حاضر هیچ تایمر فعالی برای توقف یافت نشد.')

    return redirect('home')


@login_required
def edit_time_entry(request, entry_id):
    """ویرایش یک رکورد ساعت کاری مشخص توسط کاربر صاحب آن"""
    entry = get_object_or_404(TimeEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        form = ManualTimeEntryForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'رکورد پروژه «{entry.project.name}» با موفقیت ویرایش شد.')
            return redirect('home')
    else:
        form = ManualTimeEntryForm(instance=entry, user=request.user)

    return render(request, 'edit_entry.html', {
        'form': form,
        'entry': entry,
    })


@login_required
def delete_time_entry(request, entry_id):
    """حذف ایمن یک رکورد ساعت کاری با متد POST"""
    entry = get_object_or_404(TimeEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        project_name = entry.project.name
        entry.delete()
        messages.success(request, f'رکورد مربوط به پروژه «{project_name}» حذف شد.')
    return redirect('home')


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
    total_hours = round(change_second_to_hour + change_day_to_hour, 2)
    project = None
    if query_params.get('project_id'):
        project = Project.objects.filter(id=query_params.get('project_id')).first()

    if query_params.get('export') == 'excel':
        return export_daily_report_to_excel(
            daily_report=daily_report,
            total_hours=total_hours,
            start=query_params.get('start'),
            end=query_params.get('end'),
            project=project,
        )

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
    total_hours = round(change_second_to_hour + change_day_to_hour, 2)

    project = Project.objects.get(id=project)
    base_fee = project.unit_price if project.unit_price else 300_000
    total_fee = round(total_hours * base_fee)
    return render(request, 'factor.html', {
        'total_hours': f"{total_hours:,.2f}" if total_hours % 1 != 0 else f"{int(total_hours):,}",
        "base_fee": f"{base_fee:,}",
        "total_fee": f"{total_fee:,}",
        "string_fee": f"{words(total_fee)}",
        "start_date": start,
        "end_date": end,
        "project": project,
        "invoice_number": f"{jdatetime.datetime.now().strftime('%Y%m%d')}/{random.choice([i for i in range(1, 10)])}",
        "today": jdatetime.datetime.now(),
        "user": request.user
    })


@login_required
def analytics(request):
    """صفحه گزارش تحلیلی، نمودارها و شاخص‌های کلیدی عملکرد"""
    context = get_analytics_context(request.user)
    context['chart_data'] = {
        'weekly': context['weekly_chart'],
        'projects': context['project_chart'],
        'monthly': context['monthly_chart'],
    }
    return render(request, 'analytics.html', context)

