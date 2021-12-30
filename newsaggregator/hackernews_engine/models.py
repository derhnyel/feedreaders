from django.db import models

from django.contrib.postgres.fields import ArrayField


# Create your models here.


class Items (models.Model):
    """Create Items model and specify database Columns"""
    type = models.CharField(max_length=15,null=True)
    source = models.CharField(max_length=15,null=True)
    title = models.CharField(max_length=200,null=True)
    time = models.DateTimeField(blank=True,null=True)
    text = models.TextField(blank=True,null=True)
    id = models.IntegerField(primary_key=True)
    deleted = models.BooleanField(blank=True,null=True)
    by = models.CharField(max_length=64,blank=True,null=True)
    dead = models.BooleanField(blank=True,null=True)
    descendants =  models.IntegerField(blank=True,null=True)
    url = models.URLField(blank=True,null=True)
    parent = models.IntegerField(blank=True,null=True)
    score = models.IntegerField(blank=True,null=True)
    parts = ArrayField(models.IntegerField(),blank=True,null=True)
    kids = ArrayField(models.IntegerField(),blank=True,null=True)
    date_fetched = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "{}".format((self.id,self.type,self.title,self.descendants,self.parent,
        self.by,self.score,self.url,self.text))


class Posts(models.Model):
    """Create Post model and specify database Columns"""
    type = models.CharField(max_length=15, default='story', editable=False)
    source = models.CharField(max_length=15,null=True,default='new', editable=False)
    title = models.CharField(max_length=200)
    text = models.TextField(blank=True,null=True)
    by = models.CharField(max_length=200,default='auth user', editable=False)
    url = models.URLField()
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "{}".format((self.type,self.title,self.by,self.url,self.text))    




