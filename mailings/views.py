from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ClientForm, MailingForm, MessageForm
from .models import Client, Mailing, MailingLog, Message
from .services import send_mailing


def client_list(request):
    clients = Client.objects.all()
    return render(request, "mailings/client_list.html", {"clients": clients})


def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm()
    return render(request, "mailings/client_form.html", {"form": form})


def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm(instance=client)
    return render(request, "mailings/client_form.html", {"form": form})


def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        return redirect("client_list")
    return render(request, "mailings/client_confirm_delete.html", {"client": client})


def message_list(request):
    messages = Message.objects.all()
    return render(request, "mailings/message_list.html", {"messages": messages})


def message_create(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("message_list")
    else:
        form = MessageForm()
    return render(request, "mailings/message_form.html", {"form": form})


def message_update(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.method == "POST":
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect("message_list")
    else:
        form = MessageForm(instance=message)
    return render(request, "mailings/message_form.html", {"form": form})


def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.method == "POST":
        message.delete()
        return redirect("message_list")
    return render(request, "mailings/message_confirm_delete.html", {"message": message})


def mailing_list(request):
    mailings = Mailing.objects.all()
    return render(request, "mailings/mailing_list.html", {"mailings": mailings})


def mailing_create(request):
    if request.method == "POST":
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("mailing_list")
    else:
        form = MailingForm()
    return render(request, "mailings/mailing_form.html", {"form": form})


def mailing_update(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == "POST":
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            return redirect("mailing_list")
    else:
        form = MailingForm(instance=mailing)
    return render(request, "mailings/mailing_form.html", {"form": form})


def mailing_delete(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == "POST":
        mailing.delete()
        return redirect("mailing_list")
    return render(request, "mailings/mailing_confirm_delete.html", {"mailing": mailing})


@require_POST  # Разрешаем только POST-запросы
def send_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    try:
        send_mailing(mailing.id)  # Ваша функция отправки
        messages.success(request, f"Рассылка #{pk} успешно отправлена!")
    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")
    return redirect("mailing_list")  # Перенаправляем обратно


def mailing_logs(request, mailing_id):
    logs = MailingLog.objects.filter(mailing_id=mailing_id)
    return render(request, "mailings/mailing_logs.html", {"logs": logs})


def home(request):
    context = {
        "total_mailings": Mailing.get_total_count(),
        "active_mailings": Mailing.get_active_count(),
        "unique_clients": Client.get_unique_recipients_count(),
    }
    return render(request, "mailings/home.html", context)
