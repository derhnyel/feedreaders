#import your model
from rest_framework import serializers
from .models import Items,Posts

class ItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Items
        fields = ['type','source','title','time','text','id','deleted','by','dead','descendants','url','parent','score','kids','date_fetched','top']

class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['type','source','title','text','by','url','time'] 

