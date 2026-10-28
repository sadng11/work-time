"""
سرویس محاسبات آماری، شاخص‌های کلیدی (KPI) و داده‌های نمودارها برای صفحه تحلیل کارکرد
"""
import jdatetime
from django.db.models import Sum
from .models import TimeEntry, Project


def get_analytics_context(user):
    """
    محاسبه شاخص‌های آماری و داده‌های آماده برای رندر در Chart.js
    """
    today = jdatetime.date.today()
    start_of_month = jdatetime.date(today.year, today.month, 1)

    # تمام رکوردهای بسته شده ماه جاری
    month_entries = list(
        TimeEntry.objects.filter(
            user=user,
            exit_time__isnull=False,
            entry_time__date__gte=start_of_month,
            entry_time__date__lte=today,
        ).select_related('project')
    )

    # -------------------------------------------------------------
    # ۱. شاخص‌های کلیدی ماه جاری (Monthly KPIs)
    # -------------------------------------------------------------
    total_month_seconds = sum(
        (e.duration.total_seconds() for e in month_entries if e.duration), 0.0
    )
    total_month_hours = round(total_month_seconds / 3600, 2)

    active_days_set = set(e.entry_time.date() for e in month_entries if e.entry_time)
    active_work_days = len(active_days_set)
    daily_avg_hours = (
        round(total_month_hours / active_work_days, 2) if active_work_days > 0 else 0.0
    )

    # پرکارترین روز ماه
    day_seconds_map = {}
    project_seconds_map = {}
    project_income_map = {}
    total_month_income = 0

    for e in month_entries:
        if not e.duration:
            continue
        sec = e.duration.total_seconds()
        hrs = sec / 3600
        d = e.entry_time.date()
        day_seconds_map[d] = day_seconds_map.get(d, 0.0) + sec

        proj = e.project
        proj_name = proj.name
        project_seconds_map[proj_name] = project_seconds_map.get(proj_name, 0.0) + sec

        rate = proj.unit_price if proj.unit_price else 300_000
        fee = round(hrs * rate)
        project_income_map[proj_name] = project_income_map.get(proj_name, 0) + fee
        total_month_income += fee

    if day_seconds_map:
        busiest_date = max(day_seconds_map, key=day_seconds_map.get)
        b_hours = round(day_seconds_map[busiest_date] / 3600, 2)
        persian_weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']
        day_name = persian_weekdays[busiest_date.weekday()]
        busiest_day_label = f"{day_name} {busiest_date.day} {busiest_date.j_months_fa[busiest_date.month - 1]} ({b_hours} ساعت)"
    else:
        busiest_day_label = "ثبت نشده"

    if project_income_map:
        top_project_name = max(project_income_map, key=project_income_map.get)
        top_project_income = project_income_map[top_project_name]
    else:
        top_project_name = "ثبت نشده"
        top_project_income = 0

    # -------------------------------------------------------------
    # ۲. داده‌های نمودار ۱: کارکرد ۷ روز گذشته (Weekly Bar Chart)
    # -------------------------------------------------------------
    weekly_labels = []
    weekly_hours = []
    persian_weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']

    # واکشی تمام رکوردهای ۷ روز اخیر
    seven_days_ago = today - jdatetime.timedelta(days=6)
    recent_entries = list(
        TimeEntry.objects.filter(
            user=user,
            exit_time__isnull=False,
            entry_time__date__gte=seven_days_ago,
            entry_time__date__lte=today,
        )
    )

    for i in range(6, -1, -1):
        target_date = today - jdatetime.timedelta(days=i)
        w_name = persian_weekdays[target_date.weekday()]
        lbl = f"{w_name} {target_date.day} {target_date.j_months_fa[target_date.month - 1]}"
        weekly_labels.append(lbl)

        day_entries = [e for e in recent_entries if e.entry_time and e.entry_time.date() == target_date]
        day_sec = sum((e.duration.total_seconds() for e in day_entries if e.duration), 0.0)
        weekly_hours.append(round(day_sec / 3600, 2))

    # -------------------------------------------------------------
    # ۳. داده‌های نمودار ۲: سهم پروژه‌ها در ماه جاری (Donut Chart)
    # -------------------------------------------------------------
    project_labels = []
    project_hours = []
    project_percentages = []
    colors_palette = [
        '#059669',  # Emerald
        '#2563eb',  # Blue
        '#d97706',  # Amber
        '#7c3aed',  # Violet
        '#0891b2',  # Cyan
        '#db2777',  # Pink
        '#4b5563',  # Gray
    ]

    project_items = []
    for idx, (p_name, p_sec) in enumerate(sorted(project_seconds_map.items(), key=lambda x: x[1], reverse=True)):
        p_hrs = round(p_sec / 3600, 2)
        project_labels.append(p_name)
        project_hours.append(p_hrs)
        pct = round((p_sec / total_month_seconds) * 100, 1) if total_month_seconds > 0 else 0.0
        project_percentages.append(pct)
        color = colors_palette[idx % len(colors_palette)]
        project_items.append({
            'label': p_name,
            'hours': p_hrs,
            'percentage': pct,
            'color': color,
        })

    # -------------------------------------------------------------
    # ۴. داده‌های نمودار ۳: مقایسه و روند ۶ ماه اخیر (Monthly Trend)
    # -------------------------------------------------------------
    monthly_labels = []
    monthly_hours = []
    monthly_income = []

    months_list = []
    curr_y = today.year
    curr_m = today.month
    for _ in range(6):
        months_list.append((curr_y, curr_m))
        curr_m -= 1
        if curr_m == 0:
            curr_m = 12
            curr_y -= 1
    months_list.reverse()

    first_y, first_m = months_list[0]
    six_months_ago_start = jdatetime.date(first_y, first_m, 1)

    six_month_entries = list(
        TimeEntry.objects.filter(
            user=user,
            exit_time__isnull=False,
            entry_time__date__gte=six_months_ago_start,
            entry_time__date__lte=today,
        ).select_related('project')
    )

    for y, m in months_list:
        sample_date = jdatetime.date(y, m, 1)
        m_label = f"{sample_date.j_months_fa[m - 1]} {y}"
        monthly_labels.append(m_label)

        m_entries = [
            e for e in six_month_entries
            if e.entry_time and e.entry_time.year == y and e.entry_time.month == m
        ]
        m_sec = sum((e.duration.total_seconds() for e in m_entries if e.duration), 0.0)
        m_hrs = round(m_sec / 3600, 2)
        monthly_hours.append(m_hrs)

        m_inc = 0
        for e in m_entries:
            if not e.duration:
                continue
            rate = e.project.unit_price if e.project.unit_price else 300_000
            m_inc += round((e.duration.total_seconds() / 3600) * rate)
        monthly_income.append(m_inc)

    current_month_name = f"{today.j_months_fa[today.month - 1]} {today.year}"

    return {
        'current_month_name': current_month_name,
        'kpi': {
            'total_month_hours': total_month_hours,
            'daily_avg_hours': daily_avg_hours,
            'active_work_days': active_work_days,
            'busiest_day_label': busiest_day_label,
            'total_month_income': total_month_income,
            'top_project_name': top_project_name,
            'top_project_income': top_project_income,
        },
        'weekly_chart': {
            'labels': weekly_labels,
            'hours': weekly_hours,
        },
        'project_chart': {
            'labels': project_labels,
            'hours': project_hours,
            'percentages': project_percentages,
            'colors': colors_palette[:len(project_labels)],
            'items': project_items,
        },
        'monthly_chart': {
            'labels': monthly_labels,
            'hours': monthly_hours,
            'income': monthly_income,
        },
    }
