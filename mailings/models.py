from django.db import models

from mailing_service import settings
from users.models import User


class Client(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="clients", verbose_name="Владелец"
    )
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=150, verbose_name="ФИО")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    @classmethod
    def get_unique_recipients_count(cls):
        """Количество уникальных клиентов для всех рассылок"""
        return cls.objects.distinct().count()


class Message(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        null=False,
    )
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mailings", verbose_name="Владелец"
    )
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        "Message", on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    clients = models.ManyToManyField("Client", verbose_name="Получатели")

    def __str__(self):
        return f"Рассылка #{self.id} ({self.status})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    @classmethod
    def get_total_count(cls):
        """Общее количество рассылок"""
        return cls.objects.count()

    @classmethod
    def get_active_count(cls):
        """Количество активных рассылок"""
        return cls.objects.filter(status="started").count()


class MailingLog(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    server_response = models.TextField(blank=True, verbose_name="Ответ сервера")
    mailing = models.ForeignKey(
        "Mailing", on_delete=models.CASCADE, verbose_name="Рассылка"
    )
    client = models.ForeignKey(
        "Client", on_delete=models.CASCADE, verbose_name="Клиент"
    )

    def __str__(self):
        return f"Попытка #{self.id} ({self.status})"

    class Meta:
        verbose_name = "Лог рассылки"
        verbose_name_plural = "Логи рассылок"
