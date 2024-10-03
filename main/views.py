from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.db import transaction

from django.contrib.auth import get_user_model  # Preferred method for custom User models

from .models import Ticket, Attachment, FollowUp
from .forms import (
    UserSettingsForm,
    TicketCreateForm,
    TicketEditForm,
    FollowupForm,
    AttachmentForm
)

import logging

logger = logging.getLogger(__name__)

# Get the User model
User = get_user_model()


@login_required
def inbox_view(request):
    """
    Display tickets that are assigned and unassigned.
    """
    try:
        # Optimize by querying tickets directly without fetching all users
        tickets_unassigned = Ticket.objects.exclude(assigned_to__isnull=False)
        tickets_assigned = Ticket.objects.filter(assigned_to__isnull=False)
    except Exception as e:
        logger.error(f"Error fetching tickets in inbox_view: {e}")
        tickets_unassigned = []
        tickets_assigned = []

    context = {
        "tickets_assigned": tickets_assigned,
        "tickets_unassigned": tickets_unassigned,
    }
    return render(request, 'main/inbox.html', context)


@login_required
def my_tickets_view(request):
    """
    Display tickets assigned to the current user and tickets waiting for the user.
    """
    try:
        tickets = Ticket.objects.filter(
            assigned_to=request.user
        ).exclude(status__exact="DONE")

        tickets_waiting = Ticket.objects.filter(
            waiting_for=request.user,
            status__exact="WAITING"
        )
    except Exception as e:
        logger.error(f"Error fetching tickets in my_tickets_view: {e}")
        tickets = []
        tickets_waiting = []

    context = {
        "tickets": tickets,
        "tickets_waiting": tickets_waiting
    }
    return render(request, 'main/my-tickets.html', context)


@login_required
def all_tickets_view(request):
    """
    Display all open tickets excluding those with status "DONE".
    """
    try:
        tickets_open = Ticket.objects.exclude(status__exact="DONE")
    except Exception as e:
        logger.error(f"Error fetching tickets in all_tickets_view: {e}")
        tickets_open = []

    context = {
        "tickets": tickets_open,
    }
    return render(request, 'main/all-tickets.html', context)


@login_required
def archive_view(request):
    """
    Display all closed tickets with status "DONE".
    """
    try:
        tickets_closed = Ticket.objects.filter(status__exact="DONE")
    except Exception as e:
        logger.error(f"Error fetching tickets in archive_view: {e}")
        tickets_closed = []

    context = {
        "tickets": tickets_closed,
    }
    return render(request, 'main/archive.html', context)


@login_required
def usersettings_update_view(request):
    """
    Update user settings.
    """
    user = request.user

    if request.method == 'POST':
        form_user = UserSettingsForm(request.POST, instance=user)

        if form_user.is_valid():
            form_user.save()
            next_url = request.GET.get('next', reverse('inbox'))
            return HttpResponseRedirect(next_url)
    else:
        form_user = UserSettingsForm(instance=user)

    context = {
        'form_user': form_user,
    }
    return render(request, 'main/settings.html', context)


@login_required
@transaction.atomic
def ticket_create_view(request):
    """
    Create a new ticket.
    """
    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.owner = request.user
            ticket.status = "TODO"
            ticket.save()
            return redirect('inbox')
    else:
        form = TicketCreateForm()

    context = {
        'form': form,
    }
    return render(request, 'main/ticket_edit.html', context)


@login_required
@transaction.atomic
def ticket_edit_view(request, pk):
    """
    Edit an existing ticket.
    """
    ticket = get_object_or_404(Ticket, id=pk)

    if request.method == 'POST':
        form = TicketEditForm(request.POST, instance=ticket)
        if form.is_valid():
            updated_ticket = form.save(commit=False)
            if updated_ticket.status == "DONE" and ticket.status != "DONE":
                updated_ticket.closed_date = timezone.now()
            updated_ticket.save()
            return redirect('inbox')
    else:
        form = TicketEditForm(instance=ticket)

    context = {
        'form': form,
    }
    return render(request, 'main/ticket_edit.html', context)


@login_required
def ticket_detail_view(request, pk):
    """
    View details of a specific ticket, including attachments and follow-ups.
    """
    ticket = get_object_or_404(Ticket, id=pk)
    attachments = Attachment.objects.filter(ticket=ticket)
    followups = FollowUp.objects.filter(ticket=ticket).order_by('-modified')

    context = {
        'ticket': ticket,
        'attachments': attachments,
        'followups': followups,
    }
    return render(request, 'main/ticket_detail.html', context)


@login_required
@transaction.atomic
def followup_create_view(request):
    """
    Create a new follow-up for a ticket.
    """
    if request.method == 'POST':
        form = FollowupForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.user = request.user
            followup.save()

            ticket = followup.ticket
            notification_subject = f"[#{ticket.id}] New follow-up"
            notification_body = (
                f"Hi,\n\nNew follow-up created for ticket #{ticket.id} "
                f"(http://localhost:8000/ticket/{ticket.id}/)\n\n"
                f"Title: {form.cleaned_data['title']}\n\n"
                f"{form.cleaned_data['text']}"
            )

            try:
                send_mail(
                    notification_subject,
                    notification_body,
                    'test@test.tld',
                    [ticket.owner.email],
                    fail_silently=False
                )
                logger.info(f"Follow-up email sent to {ticket.owner.email} for ticket #{ticket.id}")
            except Exception as e:
                logger.error(f"Failed to send follow-up email: {e}")

            return redirect('inbox')
    else:
        ticket_id = request.GET.get('ticket')
        user = request.user
        form = FollowupForm(initial={'ticket': ticket_id, 'user': user})

    context = {
        'form': form,
    }
    return render(request, 'main/followup_edit.html', context)


@login_required
@transaction.atomic
def followup_edit_view(request, pk):
    """
    Edit an existing follow-up.
    """
    followup = get_object_or_404(FollowUp, id=pk)

    if request.method == 'POST':
        form = FollowupForm(request.POST, instance=followup)
        if form.is_valid():
            form.save()
            return redirect('inbox')
    else:
        form = FollowupForm(instance=followup)

    context = {
        'form': form,
    }
    return render(request, 'main/followup_edit.html', context)


@login_required
@transaction.atomic
def attachment_create_view(request):
    """
    Create a new attachment for a ticket.
    """
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            ticket_id = request.GET.get('ticket')
            ticket = get_object_or_404(Ticket, id=ticket_id)
            attachment = form.save(commit=False)
            attachment.ticket = ticket
            attachment.filename = request.FILES['file'].name
            attachment.user = request.user
            attachment.save()
            return redirect('inbox')
    else:
        form = AttachmentForm()

    context = {
        'form': form,
    }
    return render(request, 'main/attachment_add.html', context)