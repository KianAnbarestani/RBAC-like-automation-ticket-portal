from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
import main.views

urlpatterns = [
    # Authentication URLs
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # User Settings
    path('settings/', login_required(main.views.usersettings_update_view), name='user-settings'),

    # Django Admin
    path('admin/', admin.site.urls),

    # Ticket URLs
    path('ticket/new/', login_required(main.views.ticket_create_view), name='ticket_new'),
    path('ticket/edit/<int:pk>/', login_required(main.views.ticket_edit_view), name='ticket_edit'),
    path('ticket/<int:pk>/', login_required(main.views.ticket_detail_view), name='ticket_detail'),

    # FollowUp URLs
    path('followup/new/', login_required(main.views.followup_create_view), name='followup_new'),
    path('followup/edit/<int:pk>/', login_required(main.views.followup_edit_view), name='followup_edit'),

    # Attachment URLs
    path('attachment/new/', login_required(main.views.attachment_create_view), name='attachment_new'),

    # Ticket Overviews
    path('inbox/', login_required(main.views.inbox_view), name='inbox'),
    path('my-tickets/', login_required(main.views.my_tickets_view), name='my-tickets'),
    path('all-tickets/', login_required(main.views.all_tickets_view), name='all-tickets'),
    path('archive/', login_required(main.views.archive_view), name='archive'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
