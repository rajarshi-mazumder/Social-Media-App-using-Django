from unicodedata import name
from django.urls import path
from . import views
# from .views import HomeView

urlpatterns = [
    #     path('', views.home, name='home-page'),
    path('', views.home_timeline, name='home-page'),
    path('', views.home_timeline, name='expanded-post-page'),
    path('post/<int:post_id>', views.post_details, name='post-page'),
    path('add_post', views.add_post, name='add-post'),
    path('add_image_post', views.add_image_post, name="add-image-post"),
    path('add_video_post', views.add_video_post, name="add-video-post"),
    path('post/edit/<int:post_id>', views.edit_post, name='edit-post'),
    path('post/edit_images/<int:post_id>',
         views.edit_image_post, name='edit-image-post'),
    path('post/edit_video/<int:post_id>',
         views.edit_video_post, name='edit-video-post'),
    path('post/delete/<int:post_id>', views.delete_post, name='delete-post'),
    path('category/<str:cat>/', views.category, name='posts-by-category'),
    # path('like/', views.like_post, name='like-post'),
    # path('like/<int:pk>', views.like_post_details, name='like-post-details'),
    path('like/', views.like, name='like'),
    path('setLikes/', views.set_likes, name='set_likes'),
    path('updateSession/', views.update_session, name='update_session'),
    path('getSessionData/', views.get_session_data, name='get_session_data'),
    path('getPostData/', views.get_post_data, name='get_post_data'),
    path('post/reply/<int:pk>', views.add_reply, name='add-reply'),
    path('post/image_reply/<int:pk>',
         views.add_image_reply, name='add-image-reply'),
    path('post/video_reply/<int:pk>',
         views.add_video_reply, name='add-video-reply'),
    # path('', HomeView.as_view(), name='home-page'),
    # REST API views
    path('posts', views.post_list_view, name='post-list-view'),
    #     path('', views.home_view, name='home-page'),
    path('getPosts/', views.getPosts, name='get-posts-rest'),
    path('getPosts/<int:pk>', views.getPost, name='get-post-rest'),
    path('getPosts/<int:pk>/update', views.updatePost, name='update-post-rest'),
    path('getPosts/<int:pk>/delete', views.deletePost, name='delete-post-rest'),
]
