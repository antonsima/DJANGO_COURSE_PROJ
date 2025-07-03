from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views
from .views import (ClientCreateView, ClientDeleteView, ClientListView, ClientUpdateView, HomeView, MailingCreateView,
                    MailingDeleteView, MailingListView, MailingLogsView, MailingUpdateView, MessageCreateView,
                    MessageDeleteView, MessageListView, MessageUpdateView, SendMailingView, CompleteMailingView,
                    UserListView, BlockUserView, UnblockUserView)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/edit/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_update"),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing_update"),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path("mailings/<int:pk>/send/", SendMailingView.as_view(), name="send_mailing"),
    path(
        "mailings/<int:mailing_id>/logs/",
        MailingLogsView.as_view(),
        name="mailing_logs",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("stats/", views.StatsView.as_view(), name="mailing_stats"),
    path('mailing/complete/<int:pk>/', CompleteMailingView.as_view(), name='complete_mailing'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/block/<int:pk>/', BlockUserView.as_view(), name='block_user'),
    path('users/unblock/<int:pk>/', UnblockUserView.as_view(), name='unblock_user'),
]
