from __future__ import absolute_import

try:
    from django.conf.urls import patterns, include, url
except:
    from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r"^events/$", "django_sendgrid.views.listener", name="sendgrid_post_event"),
    url(r"^messages/(?P<message_id>[-\w]+)/attachments/$",
        "django_sendgrid.views.download_attachments",
        name="sendgrid_download_attachments"
    ),
)
