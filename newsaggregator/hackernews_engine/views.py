from .models import Items,Posts
from .serializer import ItemsSerializer,PostsSerializer
from rest_framework import status
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.views.generic.list import ListView
from itertools import chain
from django.template import RequestContext

def handler404(request):
    response = render('404.html', {},
                              context_instance=RequestContext(request))
    response.status_code = 404
    return response
def index(request):
    return redirect('stories:new_stories')

def NewStoriesView(request):
    pages_data = get_loader(request,'new')
    return render(request,'home.html',{'numbers': pages_data,})

def merge_models(source=None,title=None):
    if title != None:
        posts = Posts.objects.filter(title=title).all().order_by('-time')
        items = Items.objects.filter(title=title).all().order_by('-time')
    elif source != None:
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



         

def initialize(source):
    cached_ids = cache.get("cached_{source}_ids".format(source=source))
    db_ids = Items.objects.values_list('id',flat=True)
    #loop = asyncio.get_event_loop()
    if cached_ids == None and db_ids.exists():
       if source == 'top':
           items = Items.objects.filter(top=True).all().order_by('date_fetched')
           return items
       elif source in ['comment','new','job']:
           items = Items.objects.filter(source=source).all().order_by('-time')
           #items = merge_models(source=source)
           return items
           
    if cache != None and db_ids.exists():
        items = [Items.objects.get(id=id) for id in cached_ids]
        return items

    return []    


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
    paginate_by = 15
    context_object_name = 'numbers'
    template_name = 'home.html'
    def get_queryset(self):
        queryset = initialize('job')
        return queryset


class ListCommentView(ListView):
    model = Items
    paginate_by = 5
    context_object_name = 'numbers'
    template_name = 'home.html'
    def get_queryset(self):
        result = super(ListCommentView, self).get_queryset()
        query=self.request.resolver_match.kwargs.get('parent')
        if query:
            postresult = Items.objects.filter(parent=query).all().order_by('-time')
            result = postresult
        else:
            result = None
        return result    

class CommentView(ListView):
    model = Items
    template_name = 'search.html'
    context_object_name = 'all_search_results'
    paginate_by = 20
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
        if filter_param != None:
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


