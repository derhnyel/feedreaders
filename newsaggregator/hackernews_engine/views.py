from .models import Items,Posts
from .serializer import ItemsSerializer,PostsSerializer
from rest_framework import status
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from django.shortcuts import render,redirect
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.views.generic.list import ListView
#import asyncio
from collections import OrderedDict
from django.db.models.signals import post_delete, post_save
from itertools import chain
from operator import attrgetter
import time
def index(request):
    return redirect('stories:new_stories')

def NewStoriesView(request):
    pages_data = get_loader(request,'new')
    return render(request,'home.html',{'numbers': pages_data})

def merge_models(source=None,title=None):
    if title is not None:
        posts = Posts.objects.filter(title=title).all().order_by('-time')
        items = Items.objects.filter(title=title).all().order_by('-time')
    elif source is not None:
         posts = Posts.objects.filter(source=source).all().order_by('-time')
         items = Items.objects.filter(source=source).all().order_by('-time')   

    sorted_items = sorted(
        chain(posts, items),
    key=lambda item: item.time, reverse=True)
    return sorted_items
  
def get_loader(request,source):
    items_serializer= initialize(source)
    page = request.GET.get('page', 1)
    paginator = Paginator(items_serializer,5)
    try:
        num_pages = paginator.page(page)
    except PageNotAnInteger:
        num_pages = paginator.page(1)
    except EmptyPage:
        num_pages = paginator.page(paginator.num_pages)
    return num_pages       
#helpers
def get_response():
    while not (cache.get('triggertop') and cache.get('triggernew') and cache.get('triggerjob')) :
        time.sleep(5)
        pass
         

def initialize(source):
    cached_ids = cache.get("cached_{source}_ids".format(source=source))
    db_ids = Items.objects.values_list('id',flat=True)
    #loop = asyncio.get_event_loop()
    if not db_ids.exists():
        #get db signal
        wait_sync = sync_to_async(get_response(),thread_sensitive=True)
        #return None
        #loop.create_task(wait_sync())
    if cached_ids is None and db_ids.exists():
       if source is 'top':
           items = Items.objects.filter(source=source).all().order_by('date_fetched')
           #items_serializer = ItemsSerializer(items,many=True)
           #return(items_serializer.data)
           return items
       elif source in ['comment','new','job']:
           items = Items.objects.filter(source=source).all().order_by('-time')
           #items = merge_models(source=source)
           #items_serializer = ItemsSerializer(items,many=True)
           #return items_serializer.data
           return items
           
    if cache is not None and db_ids.exists():
        items = [Items.objects.get(id=id) for id in cached_ids]
        #items_serializer=ItemsSerializer(items,many=True)
        #return items_serializer.data
        return items
class SearchView(ListView):
    model = Items
    template_name = 'search.html'
    context_object_name = 'all_search_results'

    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            postresult = merge_models(title=query)
            result = postresult
        else:
            result = None
        return result
                
class TopStoriesView(ListView):
    paginate_by = 6
    paginate_orphans = 3
    #context_object_name = 'numbers'
    template_name = 'home.html'
    def get_queryset(self):
        queryset = initialize('top')
        return queryset
    def get_context_data(self, **kwargs):
        """ Facilitates pagination and post count summary"""
        context = super(TopStoriesView, self).get_context_data(**kwargs)
        context['numbers'] = context.pop('page_obj', None)
        return context    
class JobView(ListView):
    paginate_by = 5
    context_object_name = 'numbers'
    template_name = 'home.html'
    def get_queryset(self):
        queryset = initialize('job')
        return queryset

class CommentView(ListView):
    paginate_by = 5
    context_object_name = 'numbers'
    template_name = 'home.html'
    def get_queryset(self):
        queryset = initialize('comment')
        return queryset        

class PostView(APIView):
    """
    List all Post, or create a new Post.
    """
    def get(self, request, format=None):
        filter_param =request.query_params.get('filter')
        if filter_param is not None:
            try:
                posts = Posts.objects.filter(type=filter_param)
                items = Items.objects.filter(type=filter_param)
                items_serializer = ItemsSerializer(items,many=True)
                posts_serializer = PostsSerializer(posts,many=True)
                return Response(items_serializer.data+posts_serializer.data)
            except:
                raise Http404    
        posts = Posts.objects.all()
        items = Items.objects.all()
        items_serializer = ItemsSerializer(items,many=True)
        posts_serializer = PostsSerializer(posts,many=True)

        return Response(items_serializer.data+posts_serializer.data)

    def post(self, request, format=None):
        serializer = PostsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostModify(APIView):
    """
    Retrieve, update or delete a Post instance.
    """
    def get_object(self,pk):
        try:
            return Posts.objects.get(pk=pk)
        except Posts.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostsSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostsSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






# def TopStoriesView(request):
#     pages_data = get_loader(request,'top')
#     page_html = loader.render_to_string("home.html", {"numbers": pages_data})
#     output_data={
#         "stories_html": page_html,
#         "has_next": pages_data.has_next(),
#     }
#     return JsonResponse(output_data)
    #return render(request,'home.html',{'numbers': pages_data})

# def load_stories(request):
    
#     posts = initialize('new')

#     page = request.POST.get('page')
#     results_per_page = 5
#     paginator = Paginator(posts, results_per_page)
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         posts = paginator.page(2)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     # build a html posts list with the paginated posts
#     posts_html = loader.render_to_string('posts.html',{'posts': posts})
#     # package output data and return it as a JSON object
#     output_data = {
#         'posts_html': posts_html,
#         'has_next': posts.has_next(),
#         "count": len(posts),
#     }
#     return JsonResponse(output_data)

# def fake_stories(request):
#     items_serializer= initialize('new')
#     return redirect('stories')

# class NewStoriesView (ListView):
#     paginate_by = 5
#     context_object_name = 'numbers'
#     template_name = 'home.html'
#     def get_queryset(self):
#         queryset = initialize('new')
#         return queryset

#from rest_framework import viewsets
#from rest_framework.decorators import api_view

#from rest_framework import mixins
#from rest_framework import generics
# Create your views here.


# class ItemsViewset(viewsets.ModelViewSet):
#     serializer_class =ItemsSerializer
#     def get_queryset(self):
#         data = Items.objects.all()
#         return data
# def display():
#     cache.get()
#     if cached_ids is None: 
#         db_ids=Items.objects.all()[:100]
#         _id for _id in db_ids


# @api_view(['GET','POST','DELETE','PUT'])
# def _list(request,pk):
#     try:
#         snippet = Snippet.objects.get(pk=pk)
#     except Snippet.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#     if request.method =="GET":
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)
#     elif request.method == "POST":
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'PUT':
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)    

