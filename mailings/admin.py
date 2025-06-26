from django.contrib import admin
from .models import Client, Message, Mailing, MailingLog


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment')
    search_fields = ('email', 'full_name')
    list_filter = ('email',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body')
    search_fields = ('subject',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'message')
    list_filter = ('status',)
    search_fields = ('message__subject',)


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'mailing', 'client', 'status')
    list_filter = ('status', 'mailing')
    search_fields = ('client__email', 'server_response')