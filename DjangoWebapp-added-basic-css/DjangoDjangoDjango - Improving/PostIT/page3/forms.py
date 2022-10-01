
from dataclasses import fields
from email.mime import image
from django.forms import ModelForm
from matplotlib import widgets
from .models import Post, Category, ImageFiles
from django import forms


# choices = [('VALORANT', 'VALORANT'), ('CSGO', 'CSGO'), ('COD', 'COD')]
choices = Category.objects.all().values_list('name', 'name')
tags = Category.objects.all().values_list('tags', 'tags')
choice_list = []

for item in choices:
    choice_list.append(item)


class PostForm(ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ('title', 'body', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            # 'author': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'author-name', 'type': 'hidden'}),
            # 'author': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'})
        }


class PostImageForm(ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ('title', 'body', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'})
        }


class PostVideoForm(ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ('title', 'body', 'category', 'video')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            # 'author': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'author-name', 'type': 'hidden'}),
            # 'author': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'})
        }


class EditPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
        }


class EditVideoPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'category', 'video')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
        }


class EditImagePostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something here...'}),
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
        }


class ImageForm(ModelForm):
    image = forms.ImageField(
        label="Image", widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False)

    class Meta:
        model = ImageFiles
        fields = ("image",)
