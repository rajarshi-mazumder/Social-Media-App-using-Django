
from django.contrib import admin
from . models import Post, Category, Profile, Replies, ImageFiles, GameProfile

# Register your models here.

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Replies)
admin.site.register(ImageFiles)
admin.site.register(GameProfile)
