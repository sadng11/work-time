import jdatetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from timesheet.models import Project, TimeEntry
from timesheet.forms import ManualTimeEntryForm, TimeEntryForm


class TimeEntryManualAndCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')
        self.project = Project.objects.create(name='پروژه تست', user=self.user, unit_price=400000)
        self.other_project = Project.objects.create(name='پروژه کاربر دیگر', user=self.other_user)

        self.client = Client()
        self.client.login(username='tester', password='password123')

    def test_manual_time_entry_form_validation(self):
        """بررسی اعتبارسنجی فرم ثبت دستی: زمان خروج نباید قبل از زمان ورود باشد"""
        now = jdatetime.datetime.now()
        one_hour_ago = now - jdatetime.timedelta(hours=1)

        # حالت نامعتبر: زمان خروج قبل از ورود
        invalid_data = {
            'project': self.project.id,
            'entry_time': now.strftime('%Y-%m-%d %H:%M'),
            'exit_time': one_hour_ago.strftime('%Y-%m-%d %H:%M'),
            'description': 'تست زمان نامعتبر'
        }
        form = ManualTimeEntryForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

        # حالت معتبر: زمان خروج بعد از ورود
        valid_data = {
            'project': self.project.id,
            'entry_time': one_hour_ago.strftime('%Y-%m-%d %H:%M'),
            'exit_time': now.strftime('%Y-%m-%d %H:%M'),
            'description': 'تست زمان معتبر'
        }
        valid_form = ManualTimeEntryForm(data=valid_data, user=self.user)
        self.assertTrue(valid_form.is_valid())

    def test_project_queryset_filtered_by_user(self):
        """پروژه‌های فرم باید فقط شامل پروژه‌های همان کاربر باشند"""
        form = ManualTimeEntryForm(user=self.user)
        project_ids = list(form.fields['project'].queryset.values_list('id', flat=True))
        self.assertIn(self.project.id, project_ids)
        self.assertNotIn(self.other_project.id, project_ids)

    def test_home_post_manual_entry(self):
        """ثبت سابقه دستی از طریق صفحه home"""
        start = jdatetime.datetime(1403, 6, 1, 9, 0)
        end = jdatetime.datetime(1403, 6, 1, 13, 30)

        response = self.client.post(reverse('home'), {
            'action': 'manual_entry',
            'project': self.project.id,
            'entry_time': start.strftime('%Y-%m-%d %H:%M'),
            'exit_time': end.strftime('%Y-%m-%d %H:%M'),
            'description': 'کارکرد دستی گذشته'
        })
        self.assertEqual(response.status_code, 302)

        entry = TimeEntry.objects.filter(user=self.user, description='کارکرد دستی گذشته').first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.project, self.project)
        self.assertIsNotNone(entry.duration)
        # 4.5 hours = 16200 seconds
        self.assertEqual(entry.duration.seconds, 16200)

    def test_edit_time_entry(self):
        """ویرایش رکورد زمان کاری توسط صاحب رکورد"""
        start = jdatetime.datetime(1403, 6, 2, 10, 0)
        end = jdatetime.datetime(1403, 6, 2, 12, 0)
        entry = TimeEntry.objects.create(
            user=self.user,
            project=self.project,
            entry_time=start,
            exit_time=end,
            description='قبل از ویرایش'
        )

        new_end = jdatetime.datetime(1403, 6, 2, 14, 0)
        edit_url = reverse('edit_time_entry', args=[entry.id])

        # درخواست GET
        get_response = self.client.get(edit_url)
        self.assertEqual(get_response.status_code, 200)

        # درخواست POST برای ویرایش
        post_response = self.client.post(edit_url, {
            'project': self.project.id,
            'entry_time': start.strftime('%Y-%m-%d %H:%M'),
            'exit_time': new_end.strftime('%Y-%m-%d %H:%M'),
            'description': 'بعد از ویرایش'
        })
        self.assertEqual(post_response.status_code, 302)

        entry.refresh_from_db()
        self.assertEqual(entry.description, 'بعد از ویرایش')
        # مدت زمان باید از 2 ساعت به 4 ساعت به‌روزرسانی شده باشد
        self.assertEqual(entry.duration.seconds, 4 * 3600)

    def test_delete_time_entry(self):
        """حذف رکورد زمان کاری با متد POST"""
        entry = TimeEntry.objects.create(
            user=self.user,
            project=self.project,
            entry_time=jdatetime.datetime.now(),
            description='رکورد برای حذف'
        )
        delete_url = reverse('delete_time_entry', args=[entry.id])

        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TimeEntry.objects.filter(id=entry.id).exists())

    def test_cannot_edit_or_delete_other_user_entry(self):
        """کاربر نباید بتواند رکورد کاربر دیگری را ویرایش یا حذف کند"""
        other_entry = TimeEntry.objects.create(
            user=self.other_user,
            project=self.other_project,
            entry_time=jdatetime.datetime.now(),
            description='رکورد متعلق به کاربر دیگر'
        )

        edit_url = reverse('edit_time_entry', args=[other_entry.id])
        delete_url = reverse('delete_time_entry', args=[other_entry.id])

        # تلاش برای مشاهده صفحه ویرایش
        edit_response = self.client.get(edit_url)
        self.assertEqual(edit_response.status_code, 404)

        # تلاش برای حذف
        delete_response = self.client.post(delete_url)
        self.assertEqual(delete_response.status_code, 404)

        # رکورد هنوز در دیتابیس موجود است
        self.assertTrue(TimeEntry.objects.filter(id=other_entry.id).exists())

    def test_factor_page_back_to_report_link(self):
        """دکمه بازگشت در صفحه فاکتور باید به صفحه گزارش با فیلترهای مشخص شده لینک داشته باشد"""
        start_str = '1405-07-01'
        end_str = '1405-08-05'
        factor_url = reverse('factor', args=[start_str, end_str, self.project.id])

        response = self.client.get(factor_url)
        self.assertEqual(response.status_code, 200)

        expected_report_url = f"{reverse('report')}?start={start_str}&end={end_str}&project_id={self.project.id}"
        self.assertContains(response, expected_report_url)

