from django.core.mail import send_mail
from .models import Mailing, Client


def send_mailing(mailing_id):
    mailing = Mailing.objects.get(pk=mailing_id)
    clients = mailing.clients.all()

    for client in clients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email='noreply@yourdomain.com',
                recipient_list=[client.email],
                fail_silently=False,
            )
            status = 'success'
            response = 'Письмо отправлено'
        except Exception as e:
            status = 'failed'
            response = str(e)

        # Логируем попытку
        MailingLog.objects.create(
            status=status,
            server_response=response,
            mailing=mailing,
            client=client,
        )

    # Обновляем статус рассылки
    if mailing.status != 'started':
        mailing.status = 'started'
        mailing.save()