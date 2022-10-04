

from cgitb import html, reset
from dataclasses import fields
from email.mime import image
from ftplib import all_errors
from http import server
from multiprocessing import reduction
from operator import is_
import os
import re
from telnetlib import GA
import this
from tkinter import Image
from turtle import ht, pos, title
from unittest import result
from urllib.request import Request
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.generic import ListView, DetailView
from matplotlib.style import context
from . models import GameProfile, Post, Replies, ImageFiles, Profile, Tags
from . forms import EditPostForm, EditVideoPostForm, ImageForm, PostForm, PostImageForm, PostVideoForm, EditImagePostForm, GameProfileForm, MatchmakingForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template.loader import render_to_string
# Create your views here.
# Paginator stuff
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .serializers import PostSerializer
from django.core import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from itertools import chain

# def home(request):
#     object_list = Post.objects.all().order_by('-post_datetime')
#     context = {
#         'object_list': object_list
#     }
#     return render(request, 'home.html', context)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def home(request):
    object_list = Post.objects.all().order_by('-post_datetime')
    image_list = ImageFiles.objects.all()
    context = {
        'object_list': object_list,
        'image_list': image_list,
    }
    return render(request, 'home.html', context)


def home_timeline(request, post_id=None):

    object_list = Post.objects.all().order_by('-post_datetime')
    game_profiles= GameProfile.objects.all()
    tags= Tags.objects.all()
    try:
        print(request.session['post_in_view'])
    except:
        pass
    # Set up pagination
    # request.session['loaded_posts'] = object_list
    p = Paginator(object_list, 4)
    # p = Paginator(Post.objects.all().order_by('-post_datetime'), 4)
    page = request.GET.get('page')
    objects = p.get_page(page)
    a = 200
    print(objects)
    try:

        last_viewed = request.session['post_in_view']
    except:
        last_viewed = ""
    image_list = ImageFiles.objects.all()
    profiles = Profile.objects.all()
    has_images_to_show = False
    try:
        post = Post.objects.get(id=post_id)
        profile = Post.objects.get(user=post['author'])
        context = {
            'object_list': object_list,
            'image_list': image_list,
            'post': post,
            'post_id': post_id,
            'objects': objects,
            'objects': objects,
            'last_viewed': last_viewed,
            'has_images_to_show': has_images_to_show,
            'profile': profile,
        }
    except:
        context = {
            'object_list': object_list,
            'image_list': image_list,
            'objects': objects,
            'last_viewed': last_viewed,
            'has_images_to_show': has_images_to_show,
            'profiles': profiles,
            'game_profiles': game_profiles,
            'tags':tags,
        }
    return render(request, 'home_timeline.html', context)


def django_image_and_file_upload_ajax(request, pk):
    form = PostImageForm()
    imageform = ImageForm()

    post_data = return_post_data(request, pk)

    replying_to = []
    # replying_to = Post.objects.get(id=pk)
    replying_to = get_parent_post(pk, replying_to)
    replying_to = replying_to[::-1]

    replies_obj = []
    replies_to_post = []

    replies = Replies.objects.filter(reply_to=pk)

    if replies:
        print("REPLIES", replies)
        for reply in replies:
            reply_post = Post.objects.get(id=reply.post_id)
            replies_obj.append(reply_post)
        replies_to_post = replies_obj[::-1]

    context = {
        'form': form,
        'replying_to': replying_to,
        'imageform': imageform,
        'replies_to_post': replies_to_post,
    }

    context.update(post_data)
    print(context)

    if request.method == 'POST':

        form = PostImageForm(request.POST)
        files = request.FILES.getlist("image")
        if form.is_valid():

            instance = form.save(commit=False)
            instance.author = request.user
            instance.reply_to = pk
            instance.is_reply = True
            if files:
                instance.has_images = True
            else:
                instance.has_images = False
            instance.save()

            for file in files:
                ImageFiles.objects.create(post=instance, image=file)

            reply = Replies(reply_to=pk, post_id=instance.id)
            reply.save()

            return(update_replies_list(request, pk))
            # return JsonResponse({'error': False, 'message': 'Uploaded Successfully'})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    else:
        form = PostImageForm()
        imageform = ImageForm()

    return render(request, 'testt.html', context)


def ajax_replies(request, pk):
    form = PostImageForm()
    imageform = ImageForm()

    post_data = return_post_data(request, pk)

    replying_to = []
    # replying_to = Post.objects.get(id=pk)
    replying_to = get_parent_post(pk, replying_to)
    replying_to = replying_to[::-1]

    replies_obj = []
    replies_to_post = []

    replies = Replies.objects.filter(reply_to=pk)

    if replies:
        print("REPLIES", replies)
        for reply in replies:
            reply_post = Post.objects.get(id=reply.post_id)
            replies_obj.append(reply_post)
        replies_to_post = replies_obj[::-1]

    context = {
        'form': form,
        'replying_to': replying_to,
        'imageform': imageform,
        'replies_to_post': replies_to_post,
    }

    context.update(post_data)
    print(context)

    return render(request, 'ajax_replies.html', context)
    # return render(request, 'testt.html', {'a': "a"})


def save_ajax_reply(request):
    if request.method == "POST":
        print("REQUESTED USER: ", request.user)
        form = PostImageForm(request.POST)
        id = int(request.POST.get('postid'))

        print(request.POST)
        print(request.POST['title'])
        instance = Post.objects.create(title=request.POST['title'],
                                       body=request.POST['body'],
                                       category=request.POST['category'],
                                       author=request.user,
                                       reply_to=id,
                                       is_reply=True
                                       )

        reply = Replies(reply_to=id, post_id=instance.id)
        reply.save()

        context = return_post_data(request, id)
        print(context['replies'])
        print("THIS IS CONTEXT: ", context)
        # html = render_to_string('replies_list.html', context, request=request)
        is_ajax = False
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            is_ajax = True
        else:
            is_ajax = False

        # html = update_replies_list(request, id)
        return(update_replies_list(request, id))

        # return JsonResponse({'replies_list': "", 'is_ajax': is_ajax})

        # return JsonResponse({"instance": "success!!"})


def update_replies_list(request, post_id):
    replies_obj = []
    replies_to_post = []

    replies = Replies.objects.filter(reply_to=post_id)
    if replies:
        print("REPLIES", replies)
        for reply in replies:
            reply_post = Post.objects.get(id=reply.post_id)
            replies_obj.append(reply_post)
        replies_to_post = replies_obj[::-1]
        image_list = ImageFiles.objects.all()

        context = {
            'replies': replies,
            'replies_obj': replies_obj,
            'replies_to_post': replies_to_post,
            'image_list': image_list,

        }

        html = render_to_string('replies_list.html', context, request=request)
        print("HTML: ", html)
        return JsonResponse({'replies_list': html, })


def post_details(request, post_id):
    print('*********************************************************************')
    post = Post.objects.get(id=post_id)
    image_list = ImageFiles.objects.all()

    replies_obj = []
    replies_to_post = []

    replies = Replies.objects.filter(reply_to=post_id)

    if replies:
        print("REPLIES", replies)
        for reply in replies:
            reply_post = Post.objects.get(id=reply.post_id)
            replies_obj.append(reply_post)
        replies_to_post = replies_obj[::-1]
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        liked = True
    total_likes = post.total_likes()
    print("Working till here")
    parents_arr = []
    if post.is_reply:
        parents_arr = get_parent_post(post.reply_to, parents_arr)
        parents_arr = parents_arr[::-1]

    context = {
        'post': post,
        'total_likes': total_likes,
        'liked': liked,
        'replies': replies,
        'replies_obj': replies_obj,
        'replies_to_post': replies_to_post,
        'parents_arr': parents_arr,
        'image_list': image_list,

    }

    return render(request, 'post.html', context)


def return_post_data(request, post_id):
    post = Post.objects.get(id=post_id)
    image_list = ImageFiles.objects.all()

    replies_obj = []
    replies_to_post = []

    replies = Replies.objects.filter(reply_to=post_id)

    if replies:
        print("REPLIES", replies)
        for reply in replies:
            reply_post = Post.objects.get(id=reply.post_id)
            replies_obj.append(reply_post)
        replies_to_post = replies_obj[::-1]
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        liked = True
    total_likes = post.total_likes()
    print("Working till here")
    parents_arr = []
    if post.is_reply:
        parents_arr = get_parent_post(post.reply_to, parents_arr)
        parents_arr = parents_arr[::-1]

    context = {
        'post': post,
        'total_likes': total_likes,
        'liked': liked,
        'replies': replies,
        'replies_obj': replies_obj,
        'replies_to_post': replies_to_post,
        'parents_arr': parents_arr,
        'image_list': image_list,
        'last_viewed': "",

    }

    return context


def add_post(request):
    
    form = PostForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        
        form = PostForm(request.POST, request.FILES)
        # if form.is_valid():
            
            # form.save()
        
        title= request.POST['title']
        body= request.POST['body']
        category= request.POST['category']
        tags= request.POST['tags']

        new_post= Post(author= request.user,title=title, body=body, category= category)
        new_post.save()
        
        tags_arr=[]
        if len(tags)>0:
            tags_list= tags.split(",")
            

            for t in tags_list:
                if not(Tags.objects.filter(tag_name=t).exists()):
                    new_tag= Tags(tag_name= t)
                    new_tag.save()
                    Tags.objects.get(id=new_tag.id).post.add(Post.objects.get(id=new_post.id))
                    

                else:
                    Tags.objects.filter(tag_name=t).post.add(Post.objects.get(id=new_post.id))
            
            new_post.set_Tag(tags_list)
            new_post.save()
        
        
        print(new_post.id)
            # instance = form.save(commit=False)
            # instance.author = request.user
            # instance.save()

        #     return redirect('home-page')
        # else:
        #     return render(request, 'add_post.html', context)
    else:
        form = PostForm()

    return render(request, 'add_post.html', context)


def add_image_post(request):
    form = PostImageForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostImageForm(request.POST)
        files = request.FILES.getlist("image")

        tags= request.POST['tags']
        

        if form.is_valid():
            # form.save()
            
                       
            instance = form.save(commit=False)
            instance.author = request.user
            if files:
                instance.has_images = True
            else:
                instance.has_images = False
            
            instance.save()
            if len(tags)>0:
                tags_list= tags.split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):
                        new_tag= Tags(tag_name= t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(Post.objects.get(id=instance.id))
                        
                    else:
                        Tags.objects.get(tag_name=t).post.add(Post.objects.get(id=instance.id))
                
                post_obj= Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()

            for file in files:
                ImageFiles.objects.create(post=instance, image=file)

            return redirect('home-page')
        else:
            print(form.errors)
    else:
        form = PostImageForm()
        imageform = ImageForm()

    return render(request, 'add_image_post.html', {"form": form, "imageform": imageform})


def add_video_post(request):
    form = PostVideoForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostVideoForm(request.POST, request.FILES)
        tags= request.POST['tags']

        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            if request.FILES:
                instance.has_video = True
            instance.save()
            if len(tags)>0:
                tags_list= tags.split(",")

                for t in tags_list:
                    if not(Tags.objects.filter(tag_name=t).exists()):
                        new_tag= Tags(tag_name= t)
                        new_tag.save()
                        Tags.objects.get(id=new_tag.id).post.add(Post.objects.get(id=instance.id))
                        
                    else:
                        Tags.objects.get(tag_name=t).post.add(Post.objects.get(id=instance.id))
                
                post_obj= Post.objects.get(id=instance.id)
                post_obj.set_Tag(tags_list)
                post_obj.save()

            return redirect('home-page')
        else:
            return render(request, 'add_video_post.html', context)
    else:
        form = PostVideoForm()

    return render(request, 'add_video_post.html', context)


def add_reply(request, pk):
    form = PostForm()

    context = {
        'form': form,
        'pk': pk,
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.reply_to = pk
            instance.is_reply = True
            instance.save()

            reply = Replies(reply_to=pk, post_id=instance.id)
            reply.save()

            # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            # return render(request, 'post-page', pk)
            return redirect('home-page')
        else:
            replying_to = []
            replying_to = Post.objects.get(id=pk)
            context = {
                'form': form,
                'replying_to': replying_to,
                'pk': pk,

            }
            return render(request, 'add_reply.html', context)
    else:
        form = PostForm()
    replying_to = []
    # replying_to = Post.objects.get(id=pk)
    replying_to = get_parent_post(pk, replying_to)
    replying_to = replying_to[::-1]
    context = {
        'form': form,
        'replying_to': replying_to,
        'pk': pk,
    }
    return render(request, 'add_reply.html', context)


def add_image_reply(request, pk):
    form = PostImageForm()
    imageform = ImageForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostImageForm(request.POST)
        files = request.FILES.getlist("image")
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.reply_to = pk
            instance.is_reply = True
            if files:
                instance.has_images = True
            else:
                instance.has_images = False
            instance.save()

            for file in files:
                ImageFiles.objects.create(post=instance, image=file)

            reply = Replies(reply_to=pk, post_id=instance.id)
            reply.save()

            context = return_post_data(request, pk)
            return render(request, 'post.html', context)
            # return redirect(request.META.get('HTTP_REFERER'))
            # return redirect('home-page')
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            replying_to = []
            replying_to = Post.objects.get(id=pk)
            context = {
                'form': form,
                'replying_to': replying_to
            }
            return render(request, 'add_reply.html', context)
    else:
        form = PostImageForm()
        imageform = ImageForm()
    replying_to = []
    # replying_to = Post.objects.get(id=pk)
    replying_to = get_parent_post(pk, replying_to)
    replying_to = replying_to[::-1]
    context = {
        'form': form,
        'replying_to': replying_to,
        'imageform': imageform
    }
    return render(request, 'add_image_reply.html', context)


def replies_page(request, pk):
    form = PostImageForm()
    imageform = ImageForm()
    post_data = return_post_data(request, pk)
    context = {
        'form': form
    }

    replying_to = []
    # replying_to = Post.objects.get(id=pk)
    replying_to = get_parent_post(pk, replying_to)
    replying_to = replying_to[::-1]
    context = {
        'form': form,
        'replying_to': replying_to,
        'imageform': imageform
    }

    if request.method == 'POST':
        print(request.POST)

        form = PostImageForm(request.POST)
        files = request.FILES.getlist("image")
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.reply_to = pk
            instance.is_reply = True
            if files:
                instance.has_images = True
            else:
                instance.has_images = False
            instance.save()

            for file in files:
                ImageFiles.objects.create(post=instance, image=file)

            reply = Replies(reply_to=pk, post_id=instance.id)
            reply.save()

            context.update(post_data)
            return redirect(request.META.get('HTTP_REFERER'))
            # return render(request, 'replies.html', context)
            # return render(request, 'post.html', post_data)
            # return redirect(request.META.get('HTTP_REFERER'))
            # return redirect('home-page')
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            replying_to = []
            replying_to = Post.objects.get(id=pk)
            context = {
                'form': form,
                'replying_to': replying_to
            }

            context.update(post_data)
            return render(request, 'replies.html', context)
    else:
        form = PostImageForm()
        imageform = ImageForm()

    context.update(post_data)
    print(context)
    return render(request, 'replies.html', context)


def add_video_reply(request, pk):
    form = PostVideoForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostVideoForm(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.reply_to = pk
            instance.is_reply = True
            if request.FILES:
                instance.has_video = True
            instance.save()

            reply = Replies(reply_to=pk, post_id=instance.id)
            reply.save()

            context = return_post_data(request, pk)
            return render(request, 'post.html', context)
            # return redirect('home-page')
        else:
            replying_to = []
            replying_to = Post.objects.get(id=pk)
            context = {
                'form': form,
                'replying_to': replying_to
            }
            return render(request, 'add_video_reply.html', context)
    else:
        form = PostVideoForm()
    replying_to = []
    # replying_to = Post.objects.get(id=pk)
    replying_to = get_parent_post(pk, replying_to)
    replying_to = replying_to[::-1]
    context = {
        'form': form,
        'replying_to': replying_to
    }
    return render(request, 'add_video_reply.html', context)


def get_parent_post(parent_id, arr):
    parents = Post.objects.get(id=parent_id)
    if parents:
        arr.append(parents)
    if parents.is_reply:
        is_reply_to = Post.objects.get(id=parents.reply_to)
        get_parent_post(is_reply_to.id, arr)
    return arr


def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
    form = EditPostForm(request.POST or None, instance=post)
    context = {
        'post': post,
        'form': form
    }

    if form.is_valid():
        form.save()
        return redirect('home-page')
    return render(request, 'update_post.html', context)


def edit_image_post(request, post_id):
    post = Post.objects.get(id=post_id)
    form = EditImagePostForm(request.POST or None, instance=post)
    imageform = ImageForm()
    files = request.FILES.getlist("image")

    context = {
        'post': post,
        'form': form,
        'imageform': imageform
    }

    if form.is_valid():
        form.save()
        instance = form.save(commit=False)
        if files:
            instance.has_images = True
        else:
            instance.has_images = False
        instance.save()
        ImageFiles.objects.filter(post=instance).delete()
        for file in files:
            ImageFiles.objects.create(post=instance, image=file)

        return redirect('home-page')

    return render(request, 'update_image_post.html', context)


def edit_video_post(request, post_id):
    post = Post.objects.get(id=post_id)
    form = EditVideoPostForm(request.POST or None,
                             request.FILES or None, instance=post)
    context = {
        'post': post,
        'form': form
    }

    if form.is_valid():
        # form.save()
        instance = form.save(commit=False)
        if not request.FILES:
            instance.has_video = False

        instance.save()
        return redirect('home-page')
    return render(request, 'update_video_post.html', context)


def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    return redirect('home-page')


@login_required
@csrf_exempt
def like(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('postid'))
        post = get_object_or_404(Post, id=id)
        print(id)
        print(post.like_count)
        test = post.likes.filter(id=request.user.id)
        print(test)
        # print(request.POST.get('elem'))
        # request.session['post_in_view'] = id
        if post.likes.filter(id=request.user.id).exists():
            print("Exists")
            post.likes.remove(request.user)
            post.like_count -= 1
            result = post.like_count
            post.save()
        else:
            print("Doesn't exist")
            post.likes.add(request.user)
            post.like_count += 1
            result = post.like_count
            post.save()
        return JsonResponse({'result': result, })


@login_required
@csrf_exempt
def set_likes(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('postid'))
        post = get_object_or_404(Post, id=id)
        # print(id)
        # print(post.body, post.like_count)
        result = post.like_count
        # print(request.POST.get('elem'))

        return JsonResponse({'result': result, })


@login_required
@csrf_exempt
def update_session(request):
    if request.POST.get('action') == 'post':
        id = int(request.POST.get('postid'))
        request.session['post_in_view'] = id
        return JsonResponse({'id': request.session['post_in_view']})


@login_required
@csrf_exempt
def get_session_data(request):

    if request.POST.get('action') == 'post':
        id = request.session['post_in_view']
        post = get_object_or_404(Post, id=id)
        result = post.like_count
        print("Last post clicked on: ", request.session['post_in_view'])
        return JsonResponse({'result': result})


@login_required
@csrf_exempt
def get_post_data(request):
    if request.POST.get('action') == 'post':
        print("This is where it's at")
        print('*********************************************************************')
        post_id = int(request.POST.get('postid'))
        post = Post.objects.get(id=post_id)
        image_list = ImageFiles.objects.all()
        image_data = serializers.serialize('json', list(
            image_list), fields=('post', 'image'))

        request.session['post_in_view'] = post_id

        request.session.modified = True
        last_viewed = request.session['post_in_view']

        replies_obj = []
        replies_to_post = []

        replies = Replies.objects.filter(reply_to=post_id)

        if replies:
            print("REPLIES", replies)
            for reply in replies:
                reply_post = Post.objects.get(id=reply.post_id)
                replies_obj.append(reply_post)
            replies_to_post = replies_obj[::-1]
        liked = False
        if post.likes.filter(id=request.user.id).exists():
            liked = True
        total_likes = post.total_likes()
        like_count = post.like_count
        print("Working till here")
        parents_arr = []
        if post.is_reply:
            parents_arr = get_parent_post(post.reply_to, parents_arr)
            parents_arr = parents_arr[::-1]

        post_images_url = []
        if post.has_images:
            for image in image_list:
                if image.post.id == post_id:
                    post_images_url.append(image.image.url)
        post_video_url = ""
        if post.has_video:
            post_video_url = post.video.url

        print("Serialized Replies: ", serializeReplies(
            replies_to_post, image_list))
        serialized_replies = []
        serialized_replies = serializeReplies(replies_to_post, image_list)
        # replies_to_post_serialized = serializers.serialize('json', list(replies_to_post), fields=(''))
        result = {
            'body': post.body,
            'has_images': post.has_images,
            'has_video': post.has_video,
            'post_id': post_id,
            'author': post.author.username,
            'image_data': image_data,
            # 'post': post,
            'total_likes': total_likes,
            'liked': liked,
            # 'replies_to_post': replies_to_post,
            'parents_arr': parents_arr,
            'last_viewed': last_viewed,
            'post_images_url': post_images_url,
            'post_video_url': post_video_url,
            'like_count': like_count,
            'serialized_replies': serialized_replies,




        }
        # print(result)

        return JsonResponse(result)


def serializeReplies(replies_to_post, image_list):
    print("REPLIES TO POST: ", replies_to_post)
    replies_arr = []
    for reply in replies_to_post:

        author = reply.author.username
        body = reply.body
        post_id = reply.id
        like_count = reply.like_count
        has_images = reply.has_images
        has_video = reply.has_video

        reply_images_url = []
        if reply.has_images:
            for image in image_list:
                if image.post.id == post_id:
                    reply_images_url.append(image.image.url)

        reply_video_url = ""
        if reply.has_video:
            reply_video_url = reply.video.url

        reply_obj = {
            'author': author,
            'body': body,
            'post_id': post_id,
            'like_count': like_count,
            'has_images': has_images,
            'has_video': has_video,
            'reply_images_url': reply_images_url,
            'reply_video_url': reply_video_url,
        }
        replies_arr.append(reply_obj)
    return replies_arr


def category(request, cat):
    catrgory_posts = Post.objects.filter(category=cat)
    context = {
        'cat': cat.title().replace('-', ' '),
        'catrgory_posts': catrgory_posts
    }
    return render(request, 'posts_by_category.html', context)

# REST API Views


def home_view(request):
    return render(request, "api/home_view.html", status=200)


def post_list_view(request):
    object_list = Post.objects.all().order_by('-post_datetime')
    image_list = ImageFiles.objects.all()
    post_list = [{"id": x.id, "author": x.author.username, "body": x.body}
                 for x in object_list]
    data = {
        "response": post_list
    }
    return JsonResponse(data)
    return render(request, 'home.html', context)


@api_view(['GET'])
def getPosts(request):
    object_list = Post.objects.all().order_by('-post_datetime')
    serializer = PostSerializer(object_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getPost(request, pk):
    object = Post.objects.get(id=pk)
    serializer = PostSerializer(object, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
def updatePost(request, pk):
    print("Hello")
    data = request.data
    object = Post.objects.get(id=pk)
    serializer = PostSerializer(instance=object, data=data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(['DELETE'])
def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return Response('Post was deleted!')

def posts_by_user(request, user):
    if(user!='favicon.png'):
        user= User.objects.get(username=user)
        posts= Post.objects.filter(author= user)
        profile= Profile.objects.filter(user=user)[0]
        print("Profile of: ",profile.followers.count())
        
        context={'posts':posts, 'profile_owner':user, 'profile': profile}
        return render(request, 'posts_by_user.html', context)
    return render(request, 'posts_by_user.html')


@api_view(['GET','POST'])
def start_following(request, who_to_follow):
    # print(who_to_follow, request.POST['user'])
    
    profile= Profile.objects.filter(user= User.objects.get(username=request.POST['user']).id)
    profile[0].following.add(User.objects.get(username=who_to_follow))
    

    profile_followed= Profile.objects.filter(user= User.objects.get(username= who_to_follow))
    profile_followed[0].followers.add(User.objects.get(username=request.POST['user']))
    print(profile_followed, request.POST['user'])
    return Response(who_to_follow)

def create_game_profile(request, user):
    form = GameProfileForm()
    post_form= PostForm()
    
    if(user!='favicon.png'):
        user= User.objects.get(username=user)
        print(user.username)
        if(GameProfile.objects.filter(user=user.id)):
            print("Profile already exists")
            
        if(request.method== 'POST'):
                if(GameProfile.objects.filter(user=user.id)):
                    GameProfile.objects.filter(user=user.id).update(game=request.POST['game'],
                                    server=request.POST['server'], rank=request.POST['rank'])
                    
                    if len(request.POST['body'])>1:
                        print(request.POST['body'])
                        new_post= Post(title=request.POST['title'], author=user, 
                                    body=request.POST['body'], category=request.POST['game'])
                        new_post.save()
                        return redirect('home-page')

                else:
                    
                    print(request.POST)
                    new_profile= GameProfile(user= user, game=request.POST['game'], 
                                            server=request.POST['server'], rank=request.POST['rank'])
                    new_profile.save()
                    context={'form':form, 'profile':new_profile, 'post_form':post_form}

                    if len(request.POST['body'])>1:
                        print(request.POST['body'])
                        new_post= Post(title=request.POST['title'], author=user, 
                                    body=request.POST['body'], category=request.POST['game'])
                        new_post.save()
                        return redirect('home-page')
                    
                    # return render(request, 'create_gamer_profile.html', context)
                
    
    return render(request,'create_gamer_profile.html', context={'form':form, 'post_form':post_form})

def MatchmakingHome(request, user):
    form= GameProfileForm()
    print(user)
    context={'form': form}
    
    
    return render(request, 'matchmaking.html', context)

def Matchmaking_Data(request, user):
    form= GameProfileForm()

    if request.method=='POST':
        print(request.POST)
        pref_game= request.POST['game']
        pref_server= request.POST['server']
        rank= request.POST['rank']
        user_profiles=[]
        proflies=[]
        game_profiles= GameProfile.objects.filter(game=pref_game)
        for g in game_profiles:
            this_user=User.objects.get(username= g.user).id
            this_profile=(Profile.objects.filter(user=int(this_user)))
            if(this_profile):
                print(this_profile[0].bio)
                obj={'username':g.user.username,'game':g.game, 'rank':g.rank, 'server': g.server,
                'bio':this_profile[0].bio , 'profile_pic':str( this_profile[0].profile_pic), 'user_status':g.user_status}
                proflies.append(obj)
            
            
        
        print("PROFILES :", proflies)
        context={'profiles': proflies}

        html= render_to_string('matchmaking_found_list.html', context, request=request)
        print(html)
        return JsonResponse({"profiles": html})

@csrf_exempt
@api_view(['GET'])
def get_game_rank_server(request, game):
    ranks=[]
    servers=[]
    if game=="Valorant":
        ranks= GameProfile.ValorantRanks.choices
        servers= GameProfile.ValorantServers.choices
    if game=="Call of Duty":
        ranks= GameProfile.CODRanks.choices
        servers= GameProfile.CODServers.choices

    if game=="League of Legends":
        ranks= GameProfile.LOLRanks.choices
        servers= GameProfile.LOLServers.choices

    if game=="Counter Shit: GO":
        ranks= GameProfile.CSRanks.choices
        servers= GameProfile.CSServers.choices
    
    return JsonResponse({"ranks":ranks, "servers":servers})

