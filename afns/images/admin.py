from django.db import models
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.forms import TextInput

from afns.images.models import Image, ImageSubject, ImageAspectRatio, ImageSelection

admin.site.register(Image)
admin.site.register(ImageSubject)
admin.site.register(ImageAspectRatio)
admin.site.register(ImageSelection)