from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import os
import logging
from django.contrib.auth.models import Group, Permission


logger = logging.getLogger(__name__)

# Retrieve the User model. This approach supports custom user models.
User = get_user_model()

def create_groups():
    # Create groups
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    call_center_group, _ = Group.objects.get_or_create(name='Call Center')
    user_group, _ = Group.objects.get_or_create(name='Users')

    # Assign permissions to groups
    admin_permissions = Permission.objects.filter(content_type__app_label='main')
    admin_group.permissions.set(admin_permissions)
    call_center_group.permissions.set(admin_permissions)  # Call Center gets the same permissions
    user_group.permissions.clear()


class Ticket(models.Model):
    STATUS_CHOICES = (
        ('TODO', 'TODO'),
        ('IN PROGRESS', 'IN PROGRESS'),
        ('WAITING', 'WAITING'),
        ('DONE', 'DONE'),
    )

    title = models.CharField('Title', max_length=255)
    owner = models.ForeignKey(
        User,
        related_name='owned_tickets',
        blank=True,
        null=True,
        verbose_name='Owner',
        on_delete=models.SET_NULL
    )
    description = models.TextField('Description', blank=True, null=True)
    status = models.CharField(
        'Status',
        choices=STATUS_CHOICES,
        max_length=255,
        blank=True,
        null=True
    )
    waiting_for = models.ForeignKey(
        User,
        related_name='waiting_tickets',
        blank=True,
        null=True,
        verbose_name='Waiting For',
        on_delete=models.SET_NULL
    )
    # Automatically set to now when status changes to "DONE"
    closed_date = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User,
        related_name='assigned_tickets',
        blank=True,
        null=True,
        verbose_name='Assigned to',
        on_delete=models.SET_NULL
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Ticket #{self.id}: {self.title}'


class FollowUp(models.Model):
    """
    A FollowUp is a comment or update related to a specific ticket.
    """
    ticket = models.ForeignKey(
        Ticket,
        related_name='followups',
        verbose_name='Ticket',
        on_delete=models.CASCADE
    )
    date = models.DateTimeField('Date', default=timezone.now)
    title = models.CharField('Title', max_length=200)
    text = models.TextField('Text', blank=True, null=True)
    user = models.ForeignKey(
        User,
        related_name='followups',
        blank=True,
        null=True,
        verbose_name='User',
        on_delete=models.SET_NULL
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-modified']

    def __str__(self):
        return f'FollowUp #{self.id} for Ticket #{self.ticket.id}'


def attachment_path(instance, filename):
    """
    Generate a file path for uploaded attachments to organize them by ticket ID.
    Example: tickets/1/filename.ext
    """
    return os.path.join('tickets', str(instance.ticket.id), filename)


class Attachment(models.Model):
    """
    An Attachment is a file associated with a specific ticket.
    """
    ticket = models.ForeignKey(
        Ticket,
        related_name='attachments',
        verbose_name='Ticket',
        on_delete=models.CASCADE
    )
    file = models.FileField(
        'File',
        upload_to=attachment_path,
        max_length=1000
    )
    filename = models.CharField('Filename', max_length=1000)
    user = models.ForeignKey(
        User,
        related_name='attachments',
        blank=True,
        null=True,
        verbose_name='User',
        on_delete=models.SET_NULL
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'

    def __str__(self):
        return self.filename
