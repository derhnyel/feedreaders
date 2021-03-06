#from django.conf.urls import url, include
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'stories'
urlpatterns = [
    path('api/', views.PostView.as_view()),
    path('api/<int:pk>/', views.PostModify.as_view()),
    path('',views.index,name='home'),
    path('newstories',views.NewStoriesView,name='new_stories'),
    path('topstories/',views.TopStoriesView.as_view(),name='top_stories'),
    path('jobs/',views.JobView.as_view(),name='show_jobs'),
    path('comments/',views.CommentView.as_view(),name='comments'),
    path('results/', views.SearchView.as_view(), name='search'),
    path('listcomment/<int:parent>/', views.ListCommentView.as_view(), name='listcomment')

]