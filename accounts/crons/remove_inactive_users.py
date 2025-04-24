from django_cron import CronJobBase, Schedule
from accounts.models import User
from datetime import timedelta
from django.utils.timezone import now

class RemoveInactiveUsersCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']  # Run at midnight

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'accounts.remove_inactive_users_cron'  # Unique code for the cron job

    def do(self):
        one_day_ago = now() - timedelta(days=1)
        inactive_users = User.objects.filter(is_active=False, created_at__lte=one_day_ago)
        count = inactive_users.count()
        print(f"Found {count} inactive user(s).")  # Debug message
        inactive_users.delete()
        print(f"Successfully deleted {count} inactive user(s).")  # Success message