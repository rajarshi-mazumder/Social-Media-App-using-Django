
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import int_list_validator
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, date
from ckeditor.fields import RichTextField


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    tags = models.CharField(
        max_length=255, default='none')

    def save(self, *args, **kwargs):
        self.tags = self.name.replace(' ', '-').lower()
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home-page')


class Post(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    body = RichTextField(blank=True, null=True)
    # body = models.TextField()
    reply_to = models.IntegerField(null=True, blank=True, default=-1)
    is_reply = models.BooleanField(null=True, default=False, blank=True)
    post_date = models.DateField(auto_now_add=True)
    post_datetime = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, default='none')
    tags = models.CharField(
        max_length=255, default='none')
    likes = models.ManyToManyField(
        User, default=None, blank=True, related_name='posts')
    like_count = models.BigIntegerField(default='0')
    video = models.FileField(null=True, blank=True, upload_to="videos/")
    has_images = models.BooleanField(null=True, blank=True, default=False)
    has_video = models.BooleanField(null=True, blank=True, default=False)

    def liked_by(self):
        likers = []
        for a in self.likes.all():
            likers.append(a.username)
        return likers

        return ', '.join([a.username for a in self.likes.all()])
        return self.likes.all()

    @property
    def num_likes(self):
        return self.likes.all().count()

    def total_likes(self):
        return self.likes.count()

    def save(self, *args, **kwargs):
        self.tags = self.category.replace(' ', '-').lower()
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.body + ' | ' + str(self.author) + '| ' + str(self.id)

    def get_absolute_url(self):
        return reverse('post-page', args=(str(self.post_id)))


class Replies(models.Model):
    reply_to = models.IntegerField(null=True, blank=True, default=-1)
    post_id = models.IntegerField(null=True, blank=True, default=-1)

    def __str__(self):
        return str(self.reply_to)


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_pic = models.ImageField(
        null=True, blank=True, upload_to="images/profile")
    discord_link = models.CharField(max_length=255, null=True, blank=True)
    twitch_link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class ImageFiles(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='images/')


LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)

# class GameProfile(models.Model):
#     user=models.OneToOneField(User, null=True, on_delete=models.CASCADE)
