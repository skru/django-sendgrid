from __future__ import absolute_import

from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe

from django_sendgrid.models import Argument
from django_sendgrid.models import Category
from django_sendgrid.models import EmailMessage
from django_sendgrid.models import EmailMessageAttachmentsData
from django_sendgrid.models import EmailMessageBccData
from django_sendgrid.models import EmailMessageBodyData
from django_sendgrid.models import EmailMessageCcData
from django_sendgrid.models import EmailMessageExtraHeadersData
from django_sendgrid.models import EmailMessageSendGridHeadersData
from django_sendgrid.models import EmailMessageSubjectData
from django_sendgrid.models import EmailMessageToData
from django_sendgrid.models import Event
from django_sendgrid.models import EventType
from django_sendgrid.models import UniqueArgument

# TODO: move my_cms.models EmailAddress, EmailGroup into django_sendgrid
from my_cms.models import EmailAddress


DEBUG_SHOW_DATA_ADMIN_MODELS = settings.DEBUG


class ArgumentAdmin(admin.ModelAdmin):
    date_hierarchy = "creation_time"
    list_display = (
        "key", "creation_time", "last_modified_time",
        "email_message_count", "unique_arguments_count")
    readonly_fields = ("key", "email_message_count", "unique_arguments_count")
    search_fields = ("name",)

    def has_add_permission(self, request):
        return False

    def email_message_count(self, argument):
        return argument.emailmessage_set.count()

    def unique_arguments_count(self, argument):
        return argument.uniqueargument_set.count()


class CategoryAdmin(admin.ModelAdmin):
    date_hierarchy = "creation_time"
    list_display = ("name", "creation_time", "last_modified_time", "email_message_count")
    readonly_fields = ("name", "email_message_count")
    search_fields = ("name",)

    def has_add_permission(self, request):
        return False

    def email_message_count(self, category):
        return category.emailmessage_set.count()


class EmailMessageGenericDataInline(admin.TabularInline):
    model = None
    readonly_fields = ("data",)
    max_num = 1
    can_delete = False

    def has_add_permission(self, request):
        return False


class EmailMessageAttachmentsDataInline(EmailMessageGenericDataInline):
    model = EmailMessageAttachmentsData


class EmailMessageBccInline(EmailMessageGenericDataInline):
    model = EmailMessageBccData


class EmailMessageBodyDataInline(EmailMessageGenericDataInline):
    model = EmailMessageBodyData


class EmailMessageCcInline(EmailMessageGenericDataInline):
    model = EmailMessageCcData


class EmailMessageExtraHeadersDataInline(EmailMessageGenericDataInline):
    model = EmailMessageExtraHeadersData


class EmailMessageSendGridDataInline(EmailMessageGenericDataInline):
    model = EmailMessageSendGridHeadersData


class EmailMessageSubjectDataInline(EmailMessageGenericDataInline):
    model = EmailMessageSubjectData


class EmailMessageToDataInline(EmailMessageGenericDataInline):
    model = EmailMessageToData


class CategoryInLine(admin.TabularInline):
    model = EmailMessage.categories.through
    extra = 0
    can_delete = False
    readonly_fields = ("category",)

    def has_add_permission(self, request):
        return False


class EventInline(admin.TabularInline):
    model = Event
    can_delete = False
    extra = 0
    readonly_fields = ("email", "event_type")


class UniqueArgumentsInLine(admin.TabularInline):
    model = UniqueArgument
    extra = 0
    can_delete = False
    readonly_fields = ("argument", "data", "value",)

    def has_add_permission(self, request):
        return False

def show_detail(instance, eventtype):
    sg_events = instance.event_set.filter(event_type__name=eventtype)
    count = len(sg_events)
    if count >= 1:
        result = "<br><br><details><summary>x {}</summary><br><table>".format(count)
        for event in sg_events:
            if EmailAddress.objects.filter(email=event.email).exists():
                email_address = EmailAddress.objects.get(email=event.email)
                result += ("<tr><a href='{}/my_cms/emailaddress/{}/change/'>{}</a></tr><br>".
                    format(settings.ADMIN_URL, email_address.id, event.email))
            else:
                result += "<tr>{}</tr><br>".format(event.email)
        result += "</table></details>"
        return mark_safe(result)
    return mark_safe("<br><br>0")

class EmailMessageAdmin(admin.ModelAdmin):
    date_hierarchy = "creation_time"
    list_display = (
        "subject_data",
        'draft',
        "from_email",
        "to_email",
        "response",
        "creation_time",
        "recipient_count",
    )
    list_filter = ("from_email", "subject__data", "response", "draft")
    readonly_fields = (
        "from_email",
        "to_email",
        "emailgroup",
        "additional",
        "template",
        "message_id",
        "response",
        "draft",
        "body_data",
        "unknown_count",
        "deferred_count",
        "processed_count",
        "dropped_count",
        "delivered_count",
        "bounce_count",
        "open_count",
        "click_count",
        "unsubscribe_count",
        "group_unsubscribe_count",
        "spamreport_count",
    )
    exclude = ['category', 'categories', 'category_count',
        "arguments", "unique_argument_count"]

    # inlines = (
    #     EmailMessageToDataInline,
    #     EmailMessageCcInline,
    #     EmailMessageBccInline,
    #     EmailMessageSubjectDataInline,
    #     EmailMessageBodyDataInline,
    #     EmailMessageSendGridDataInline,
    #     EmailMessageExtraHeadersDataInline,
    #     EmailMessageAttachmentsDataInline,
    #     #CategoryInLine,
    #     EventInline,
    #     UniqueArgumentsInLine,
    # )
    # fieldsets = (
    #     (None, {'fields': ('username', 'password')}),
    #     (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    #     (_('Permissions'), 
    #         {'fields': (
    #             'is_active', 'is_staff', 'is_superuser',
    #             'groups', 'user_permissions')}),
    #     (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    #     (_('Orders'), {'fields': ('orders',)}),
    # )

    def has_add_permission(self, request):
        return False

    def category_count(self, emailMessage):
        return emailMessage.categories.count()

    def first_event_type(self, emailMessage):
        if emailMessage.first_event:
            return emailMessage.first_event.event_type.name
        return None

    def latest_event_type(self, emailMessage):
        if emailMessage.latest_event:
            return emailMessage.latest_event.event_type.name
        return None

    def unique_argument_count(self, emailMessage):
        return emailMessage.uniqueargument_set.count()

    def recipient_count(self, instance):
        return len(instance.to.data.split(','))
    recipient_count.short_description = 'recipient count'

    def body_data(self, instance):
        return mark_safe(
            "<br><br><details><summary>show</summary><br><div style='max-width:800px; background:white;'>{}</div></details>"
                .format(instance.body.data)
        )
    body_data.short_description = 'Content'

    def unknown_count(self, instance):
        eventtype = "UNKNOWN"
        return show_detail(instance, eventtype)
    unknown_count.short_description = 'Unknown'

    def deferred_count(self, instance):
        eventtype = "DEFERRED"
        return show_detail(instance, eventtype)
    deferred_count.short_description = 'Deferred'

    def processed_count(self, instance):
        eventtype = "PROCESSED"
        return show_detail(instance, eventtype)
    processed_count.short_description = 'Processed'

    def dropped_count(self, instance):
        eventtype = "DROPPED"
        return show_detail(instance, eventtype)
    dropped_count.short_description = 'Dropped'

    def delivered_count(self, instance):
        eventtype = "DELIVERED"
        return show_detail(instance, eventtype)
    delivered_count.short_description = 'Delivered'

    def bounce_count(self, instance):
        eventtype = "BOUNCE"
        return show_detail(instance, eventtype)
    bounce_count.short_description = 'Bounced'

    def open_count(self, instance):
        eventtype = "OPEN"
        return show_detail(instance, eventtype)
    open_count.short_description = 'Opened'

    def click_count(self, instance):
        eventtype = "CLICK"
        return show_detail(instance, eventtype)
    click_count.short_description = 'Clicked'

    def unsubscribe_count(self, instance):
        eventtype = "UNSUBSCRIBE"
        return show_detail(instance, eventtype)
    unsubscribe_count.short_description = 'Unsubscribed Globally'

    def group_unsubscribe_count(self, instance):
        eventtype = "GROUP_UNSUBSCRIBE"
        return show_detail(instance, eventtype)
    group_unsubscribe_count.short_description = 'Unsubscribed Marketing'

    def spamreport_count(self, instance):
        eventtype = "SPAMREPORT"
        return show_detail(instance, eventtype)
    spamreport_count.short_description = 'Reported as Spam'
    

class EventAdmin(admin.ModelAdmin):
    date_hierarchy = "creation_time"
    list_display = (
        "email_message",
        "event_type",
        "email",
        "creation_time",
        "last_modified_time",
    )
    list_filter = ("event_type",)
    search_fields = ("email_message__message_id",)
    readonly_fields = (
        "email_message",
        "event_type",
        "email",
        "creation_time",
        "last_modified_time",
    )

    def has_add_permission(self, request):
        return False


class EventTypeAdmin(admin.ModelAdmin):
    # date_hierarchy = "creation_time"
    list_display = ("name", "event_count")
    readonly_fields = (
        "name",
        "event_count",
    )

    def has_add_permission(self, request):
        return False

    def event_count(self, eventType):
        return eventType.event_set.count()


class EmailMessageGenericDataAdmin(admin.ModelAdmin):
    list_display = ("email_message", "data")

    def has_add_permission(self, request):
        return False


class UniqueArgumentAdmin(admin.ModelAdmin):
    date_hierarchy = "creation_time"
    list_display = ("email_message", "argument", "data", "creation_time", "last_modified_time")
    list_filter = ("argument",)
    readonly_fields = ("email_message", "argument", "data",)
    search_fields = ("argument__key", "data")

    def has_add_permission(self, request):
        return False


admin.site.register(Argument, ArgumentAdmin)
admin.site.register(UniqueArgument, UniqueArgumentAdmin)
admin.site.register(EmailMessage, EmailMessageAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Category, CategoryAdmin)

if DEBUG_SHOW_DATA_ADMIN_MODELS:
    admin.site.register(EmailMessageAttachmentsData, EmailMessageGenericDataAdmin)
    admin.site.register(EmailMessageBccData, EmailMessageGenericDataAdmin)
    admin.site.register(EmailMessageBodyData, EmailMessageGenericDataAdmin)
    admin.site.register(EmailMessageCcData, EmailMessageGenericDataAdmin)
    admin.site.register(EmailMessageSendGridHeadersData, EmailMessageGenericDataAdmin)
    admin.site.register(EmailMessageExtraHeadersData, EmailMessageGenericDataAdmin)
    admin.site.register(EmailMessageSubjectData, EmailMessageGenericDataAdmin)
    admin.site.register(EmailMessageToData, EmailMessageGenericDataAdmin)
