from django.conf import settings
from django.db import models, transaction
from django.utils import simplejson

from utils import add_unsubscribes
from utils import delete_unsubscribes
from utils import get_unsubscribes


SENDGRID_EMAIL_USERNAME = getattr(settings, "SENDGRID_EMAIL_USERNAME", None)
SENDGRID_EMAIL_PASSWORD = getattr(settings, "SENDGRID_EMAIL_PASSWORD", None)

class BulkCreateManager(models.Manager):
	@transaction.commit_on_success
	def bulk_create_with_manual_ids(self,instances):
		start = (self.all().aggregate(models.Max('pk'))['pk__max'] or 0) + 1
		for i,instance in enumerate(instances): 
			instance.pk = start + i
		instancesCreated = self.bulk_create(instances)
		for instance in instancesCreated:
			#this should possibly be abandoned for a custom bulk_post_save signal for efficiency reasons
			models.signals.post_save.send(
				sender=instance.__class__, 
				instance=instance,
				created=True, 
				raw=False,
				using='default'
			)
		return instancesCreated

class SendGridUserMixin:
	"""
	Adds SendGrid related convienence functions and properties to ``User`` objects.
	"""
	def is_unsubscribed(self):
		"""
		Returns True if the ``User``.``email`` belongs to the unsubscribe list.
		"""
		response = get_unsubscribes(email=self.email)
		results = simplejson.loads(response)
		return len(results) > 0
		
	def add_to_unsubscribes(self):
		"""
		Adds the ``User``.``email`` from the unsubscribe list.
		"""
		response = add_unsubscribes(email=self.email)
		result = simplejson.loads(response)
		return result
		
	def delete_from_unsubscribes(self):
		"""
		Removes the ``User``.``email`` from the unsubscribe list.
		"""
		response = delete_unsubscribes(email=self.email)
		result = simplejson.loads(response)
		return result