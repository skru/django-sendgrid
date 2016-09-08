from django.conf.urls import url

from main.views import send_simple_email

urlpatterns = [
    url(r'^$', send_simple_email),
]
