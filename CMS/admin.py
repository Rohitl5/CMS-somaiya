from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from .models import User,Conference,Author,Reviewer,Paper,Track,Review,committeeImages,conferenceImages,registered_authors


admin.site.register(User)
admin.site.register(Conference)
admin.site.register(Reviewer)
admin.site.register(Author)
admin.site.register(Paper)
admin.site.register(Review)
admin.site.register(Track)
admin.site.register(committeeImages)
admin.site.register(conferenceImages)
admin.site.register(registered_authors)