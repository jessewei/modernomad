from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models

'''
y syncdb w new fields (update migrations?)
y update fixtures/demo data
y test house resource
load houses from houses resource (origin issues?)
write new houses via houses resource
- creates new house object and new user object (if DNE)
authenticate to edit houses
'''

class House(models.Model):
	# meta
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	admins = models.ManyToManyField(User, blank=True, null=True)
	# location
	address = models.CharField(max_length=400, unique=True)
	latLong = models.CharField(max_length=100, unique=True)
	# community size
	residents = models.IntegerField() 
	# descriptive
	name = models.CharField(max_length=200) # required
	picture = models.ImageField(upload_to="photos/%Y/%m/%d", blank=True, null=True)
	description = models.TextField(max_length=2000, null=True, blank=True) # + suggested max length. possible things to incl. are description of mission/values, house rules etc. if desired. 
	mission_values = models.TextField(max_length=2000, null=True, blank=True) # comma separated list of tags
	amenities = models.TextField(blank=True, null=True)
	guests = models.NullBooleanField(blank=True, null=True)
	events = models.NullBooleanField(blank=True, null=True)
	events_description = models.TextField(blank=True, null=True)
	space_share = models.NullBooleanField(blank=True, null=True)
	space_share_description = models.TextField(blank=True, null=True)
	slug = models.CharField(max_length=100, unique=True, blank=True, null=True)
	contact_ok = models.NullBooleanField(blank=True, null=True)
	contact = models.emailField(blank=True, null=True) # required if contact_ok = True
	# social
	website = models.URLField(verify_exists = True, null=True, blank=True, unique=True)
	twitter_handle = models.CharField(max_length=100, null=True, blank=True)
	pictures_feed = models.CharField(max_length=400, null=True, blank=True)

	# future - mailing lists?
	# deprecated: 
	# get_in_touch = models.CharField(max_length=100, unique=True, blank=True, null=True) --> replace with "ok to contact?" + email addy
	# house_rules = models.TextField(blank=True, null=True) 

	def __unicode__(self):
		if self.name:
			return (self.name)
		else:
			return self.address

RESOURCE_TYPES = (
	('bedroom', 'bedroom'),
	('bed', 'bed'),
	('conference_room', 'conference room'),
)

class Resource(models.Model):
	house = models.ForeignKey(House)
	name = models.CharField(max_length=200)
	blurb = models.TextField()
	resource_type = models.CharField(max_length=200, choices=RESOURCE_TYPES)
	def __unicode__(self):
		return (self.name)


class UserProfile(models.Model):
	status_choices = ((u'0', 'New'), (u'1', 'Introduced'), (u'2', 'Accepted'))
	user = models.OneToOneField(User)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	# XXX upload_to will need to be a better solution eventually (s3? mongo?) 
	image = models.ImageField(upload_to="data/avatars/%Y/%m/%d/", blank=True, help_text="Leave blank to use <a href='http://gravatar.com'>Gravatar</a>")
	bio = models.TextField("A bit about yourself")
	links = models.TextField(blank=True, help_text="Comma-separated, please")
	upto = models.TextField("What are you Up To?", help_text="What are some projects you're working on? What are you up to, bigger picture?")
	# TODO (JMC): Replace with use of Django Groups
	status = models.CharField(max_length=1, choices = status_choices)
	invited_by = models.ForeignKey('self', blank=True, null=True, help_text="Your chosen reference will be asked to confirm your relationship.")

	def __unicode__(self):
		return (self.user.__unicode__())

	def save(self, *args, **kwargs):
		# for new users, set the status depending on whether they were
		# invited by someone or not
		if not self.id:
			if self.invited_by is None:
				self.status = u'0'
			else:
				self.status = u'1'
		super(UserProfile, self).save(*args, **kwargs)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
		
class Endorsement(models.Model):
	# endorsements from a person or house
	# NOTE(mdh): Currently this only supports endorsements by a house.
	endorsee = models.ForeignKey(User)
	endorser = models.ForeignKey(House)
	comment = models.TextField()

	def __unicode__(self):
		return '%s endorsed %s' % (self.endorser, self.endorsee)
