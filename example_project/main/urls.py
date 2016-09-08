from django.conf.urls import patterns, include, url

from main.views import send_simple_email

urlpatterns = [
	url(r'^$', send_simple_email),
]
