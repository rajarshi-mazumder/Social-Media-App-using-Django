

from cgitb import reset
from email.mime import image
from ftplib import all_errors
from operator import is_
import os
from tkinter import Image
from unittest import result
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.generic import ListView, DetailView
from matplotlib.style import context
from . models import Post, Replies, ImageFiles
from . forms import EditPostForm, EditVideoPostForm, ImageForm, PostForm, PostImageForm, PostVideoForm, EditImagePostForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
# Paginator stuff
from django.core.paginator import Paginator


from .serializers import PostSerializer
from django.core import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view


# def home(request):
#     object_list = Post.objects.all().order_by('-post_datetime')
#     context = {
#         'object_list': object_list
#     }
#     return render(request, 'home.html', context)


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
    try:
        print(request.session['post_in_view'])
    except:
        pass
    # Set up pagination
    p = Paginator(Post.objects.all().order_by('-post_datetime'), 4)
    page = request.GET.get('page')
    objects = p.get_page(page)
    a = 200
    print(objects)
    try:

        last_viewed = request.session['post_in_view']
    except:
        last_viewed = ""
    image_list = ImageFiles.objects.all()
    has_images_to_show = False
    try:
        post = Post.objects.get(id=post_id)
        context = {
            'object_list': object_list,
            'image_list': image_list,
            'post': post,
            'post_id': post_id,
            'objects': objects,
            'objects': objects,
            'last_viewed': last_viewed,
            'has_images_to_show': has_images_to_show,
        }
    except:
        context = {
            'object_list': object_list,
            'image_list': image_list,
            'objects': objects,
            'last_viewed': last_viewed,
            'has_images_to_show': has_images_to_show,
        }
    return render(request, 'home_timeline.html', context)


def post_details(request, post_id):
    print('*********************************************************************')
    post = Post.objects.get(id=post_id)
    image_list = ImageFiles.objects.all()

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
        'last_viewed': last_viewed,

    }

    return render(request, 'post.html', context)


def add_post(request):
    form = PostForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        print(request.POST)
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()

            return redirect('home-page')
        else:
            return render(request, 'add_post.html', context)
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
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            if files:
                instance.has_images = True
            else:
                instance.has_images = False
            instance.save()

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
        if form.is_valid():
            # form.save()
            instance = form.save(commit=False)
            instance.author = request.user
            if request.FILES:
                instance.has_video = True
            instance.save()

            return redirect('home-page')
        else:
            return render(request, 'add_video_post.html', context)
    else:
        form = PostVideoForm()

    return render(request, 'add_video_post.html', context)


def add_reply(request, pk):
    form = PostForm()
    context = {
        'form': form
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

            return redirect('home-page')
        else:
            replying_to = []
            replying_to = Post.objects.get(id=pk)
            context = {
                'form': form,
                'replying_to': replying_to
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
        'replying_to': replying_to
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

            return redirect('home-page')
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
            instance.save()

            reply = Replies(reply_to=pk, post_id=instance.id)
            reply.save()

            return redirect('home-page')
        else:
            replying_to = []
            replying_to = Post.objects.get(id=pk)
            context = {
                'form': form,
                'replying_to': replying_to
            }
            return render(request, 'add_reply.html', context)
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
    return render(request, 'add_reply.html', context)


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
            'replies_to_post': replies_to_post,
            'parents_arr': parents_arr,
            'last_viewed': last_viewed,
            'post_images_url': post_images_url,



        }
        print(result)

        return JsonResponse(result)


def category(request, cat):
    catrgory_posts = Post.objects.filter(tags=cat)
    context = {
        'cat': cat.title().replace('-', ' '),
        'catrgory_posts': catrgory_posts
    }
    return render(request, 'posts_by_category.html', context)

# class HomeView(ListView):
#     model = Post
#     template_name = 'home.html'


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
