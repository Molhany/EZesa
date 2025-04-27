
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponseRedirect  # Import HttpResponseRedirect
from .models import User, Bill, Energy, Notification, SupportTicket, Tutorial
from .forms import UserCreationForm, UserChangeForm
from django.contrib import messages

class TutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_uploaded')
    search_fields = ('title',)

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('meter_number', 'first_name', 'surname', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('meter_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'surname', 'address')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('meter_number', 'first_name', 'surname', 'address', 'password1', 'password2'),
        }),
    )
    search_fields = ('meter_number', 'first_name', 'surname')
    ordering = ('meter_number',)
    filter_horizontal = ()

    # Add the send_notification_to_all custom action
    actions = ['send_notification_to_all']

    def send_notification_to_all(self, request, queryset):
        if 'apply' in request.POST:
            message = request.POST.get('message', '')
            for user in queryset:
                Notification.objects.create(user=user, message=message)
            self.message_user(request, "Notification sent to all selected users.")
            return HttpResponseRedirect(request.get_full_path())
        else:
            return HttpResponseRedirect(request.get_full_path())

    send_notification_to_all.short_description = "Send notification to all selected users"

admin.site.register(User, UserAdmin)
admin.site.register(Bill)
admin.site.register(Energy)
admin.site.register(Notification)
admin.site.register(SupportTicket)
admin.site.register(Tutorial, TutorialAdmin)  # Register Tutorial with TutorialAdmin