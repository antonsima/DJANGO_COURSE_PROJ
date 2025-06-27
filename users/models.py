from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_blocked = models.BooleanField(default=False)

    def mailing_stats(self):
        from mailings.models import MailingLog

        return {
            "total": MailingLog.objects.filter(mailing__owner=self).count(),
            "success": MailingLog.objects.filter(
                mailing__owner=self, status="success"
            ).count(),
            "failed": MailingLog.objects.filter(
                mailing__owner=self, status="failed"
            ).count(),
        }
