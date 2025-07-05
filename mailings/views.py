from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView, View

from .forms import ClientForm, MailingForm, MessageForm
from .models import Client, Mailing, MailingLog, Message
from .services import send_mailing

User = get_user_model()


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailings/client_list.html"
    context_object_name = "clients"

    # @method_decorator(cache_page(60 * 15))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_manager():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailings/client_form.html"
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailings/client_form.html"
    success_url = reverse_lazy("client_list")

    def dispatch(self, request, *args, **kwargs):
        client = self.get_object()
        if not request.user.is_manager() and client.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailings/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")

    def dispatch(self, request, *args, **kwargs):
        client = self.get_object()
        if request.user.is_manager():
            raise PermissionDenied("Менеджеры не могут удалять клиентов")
        if client.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"

    # @method_decorator(cache_page(60 * 15))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_manager():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("message_list")

    def dispatch(self, request, *args, **kwargs):
        message = self.get_object()
        if not request.user.is_manager() and message.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("message_list")

    def dispatch(self, request, *args, **kwargs):
        message = self.get_object()
        if not request.user.is_manager() and message.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    # @method_decorator(cache_page(60 * 15))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_manager():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['user'] = self.request.user

        return form_kwargs


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailing_list")

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if not request.user.is_manager() and mailing.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if self.request.user.is_manager():
            form.instance.is_active = False  # Менеджер может только отключить
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if request.user.is_manager():
            raise PermissionDenied("Менеджеры не могут удалять рассылки")
        if mailing.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    permission_required = "users.can_block_users"

    def get_queryset(self):
        # Получаем только обычных пользователей (не модераторов и не суперпользователей)
        return User.objects.filter(
            is_superuser=False, groups__name__isnull=True
        ).exclude(pk=self.request.user.pk)


class BlockUserView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.can_block_users"

    def post(self, request, pk):
        user = get_user_model().objects.get(pk=pk)
        user.is_active = False
        user.save()
        messages.success(request, f"Пользователь {user.email} заблокирован")
        return redirect("user_list")


class UnblockUserView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.can_block_users"

    def post(self, request, pk):
        user = get_user_model().objects.get(pk=pk)
        user.is_active = True
        user.save()
        messages.success(request, f"Пользователь {user.email} разблокирован")
        return redirect("user_list")


@method_decorator(require_POST, name="dispatch")
class SendMailingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        # Проверка статуса рассылки
        if mailing.status == "completed":
            messages.warning(
                request, f"Рассылка #{pk} завершена и не может быть отправлена"
            )
            return redirect("mailing_list")

        # Проверка прав доступа
        if not request.user.is_manager() and mailing.owner != request.user:
            messages.error(request, "Нет прав для отправки этой рассылки")
            return redirect("mailing_list")

        try:
            send_mailing(mailing.id)
            messages.success(request, f"Рассылка #{pk} успешно отправлена!")
        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")

        return redirect("mailing_list")


class MailingLogsView(LoginRequiredMixin, ListView):
    template_name = "mailings/mailing_logs.html"
    context_object_name = "logs"

    # @method_decorator(cache_page(60 * 15))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        mailing_id = self.kwargs["mailing_id"]
        mailing = get_object_or_404(Mailing, pk=mailing_id)

        # Проверка прав доступа
        if not self.request.user.is_manager() and mailing.owner != self.request.user:
            raise PermissionDenied

        return MailingLog.objects.filter(mailing_id=mailing_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailing"] = get_object_or_404(Mailing, pk=self.kwargs["mailing_id"])
        return context


class HomeView(TemplateView):
    template_name = "mailings/home.html"

    # @method_decorator(cache_page(60 * 15))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total_mailings": Mailing.get_total_count(),
                "active_mailings": Mailing.get_active_count(),
                "unique_clients": Client.get_unique_recipients_count(),
            }
        )
        return context


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "mailings/stats.html"

    # @method_decorator(cache_page(60 * 15))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        total_mailings = Mailing.objects.filter(owner=user).count()

        active_mailings = Mailing.objects.filter(owner=user, status="active").count()

        logs = MailingLog.objects.filter(mailing__owner=user)
        total_attempts = logs.count()

        success_attempts = logs.filter(status="success").count()
        failed_attempts = logs.filter(status="failed").count()

        success_rate = (
            (success_attempts / total_attempts * 100) if total_attempts > 0 else 0
        )

        context["stats"] = {
            "active_mailings": active_mailings,
            "total_mailings": total_mailings,
            "total_attempts": total_attempts,
            "success_attempts": success_attempts,
            "failed_attempts": failed_attempts,
            "success_rate": success_rate,
        }
        return context


class CompleteMailingView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.can_disable_mailings"
    raise_exception = True

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = "completed"
        mailing.save()
        return redirect(reverse("mailing_list"))


class StartMailingView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.can_disable_mailings"
    raise_exception = True

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = "started"
        mailing.save()
        return redirect(reverse("mailing_list"))