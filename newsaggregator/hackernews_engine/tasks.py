from .utils import  hnapi
from django.core.cache import cache
from .models import Items
from datetime import datetime
import time



#create an instance of hacker_news_api_calls 
hacker_news = hnapi.hackernews_engine(timeout=20)
                   
def disimilar_elements(list_1,list_2):
    """Find uncommon elements in the lists"""  
    
    set_list = set(list_1) # this reduces the lookup time from O(n) to O(1)
     
    disimilar = [item for item in list_2 if item not in set_list] #list comprehension to find elements in list_2 not in list_1
    return disimilar  

def purge_similar_items(list1,list2,source):
    """Update recurrent element in fetch list in database too"""
    for elem in list1:
        if elem in list2:
            list1.remove(elem)
            Items.objects.filter(pk=elem).update(source=source)
    return list1


def get_comments(_list):
    """Get comments id (kids) in story items and fetch the comments items"""
    comments_items = [hacker_news.get_item(comment_id) for comment_id in _list]
    return comments_items       

def fetch_items(fetched_ids,cache_key,source):
    """Perform checks and Fetch ids and items from Api"""
    print('Fetched ids {source} : {ids}'.format(source=source,ids=len(fetched_ids) if fetched_ids is not None else None ))    
    cached_ids = cache.get(cache_key) #get cached ids
    print('Cached ids {source} : {ids}'.format(source=source,ids=len(cached_ids) if cached_ids is not None else None ))

    #cache_count = cache.get('count'+source) #get cached count
    #print('Cache Count {source} : {ids}'.format( source=source, ids=cache_count))

    db_ids = Items.objects.values_list('id',flat=True) # get database ids
    print('Stored Database IDS {source} : {ids} '.format(source=source, ids=len(db_ids)))

    if cached_ids is None and db_ids.exists(): #web app restarted and Database has objects or a cache hot reload
        #fetched_ids=fetched_ids[:100] #fetch 100 items
        new_ids=disimilar_elements(db_ids,fetched_ids)#get ids in fetched_ids that are not in database_ids
        #new_ids = purge_similar_items(new_ids,db_ids,source)
        new_items= [hacker_news.get_item(_id) for _id in new_ids]# get item list by id from api 
        #cache.set('count'+source,1) #set count to 1    
        return new_items,fetched_ids
    
    elif not db_ids.exists() and cached_ids is None: #At first Start .. Initialization of db
        #fetched_ids=fetched_ids[:100]#fetch top 100 ids to reduces processing time
        items = [hacker_news.get_item(_id) for _id in fetched_ids] #fetch items using fetched ids from api
        #cache.set('count'+source,1) # set count to 1 
        return items,fetched_ids
    
    elif cached_ids is not None: #cache contains previous fetched results
        
        #set slice to incrementally fetch 100 ids and items until the default api 500 ids response and cache is full 
        # try:
        #     if cache_count<=4:       
        #       id_slice=cache_count*100
        #       fetched_ids=fetched_ids[:id_slice]
        # except:
        #     cache.delete('count'+source)
        #     cache.set('count'+source,5)    
        new_ids = disimilar_elements(cached_ids,fetched_ids)#find new ids in fetched ids not in cached ids
        new_ids = purge_similar_items(new_ids,db_ids,source) #remove items added to database in the past from cache
        new_items = [hacker_news.get_item(_id) for _id in new_ids] #get items
        return new_items,fetched_ids   


def create_pk(new_items,fetched_ids,source):
    """Create model object instance for all new ids as primary key"""
    for item in  new_items:
      try:
        if item['type'] not in ['unknown',None]:
            if source is not 'comment':
                Items.objects.create(id=item['id'],source=source)#create each model object instance
            else:
                Items.objects.create(id=item['id'],source=source,parent=item['parent'])    
      except:
          fetched_ids.remove(item['id'])
    return fetched_ids    


def rearrange_db(_list):
    try:
        for id in _list.reverse():
            Items.objects.filter(pk=id).update(date_fetched=datetime.now())
    except:pass        
    

def update_items(source,id_list=None):
    """Save items to database"""
    print('Starting task to fetch and store {source} items...'.format(source=source))
    cache.delete('trigger{}'.format(source))
    cache.set('trigger{}'.format(source),False)
    #get top or new stories
    comments=[]
    if source is 'top':
        fetched_ids = hacker_news.get_top_stories()[:100] 
    elif source is 'new':
        fetched_ids=hacker_news.get_new_stories()[:100] 
    elif source is 'job':
        fetched_ids= hacker_news.get_jobs()
    elif source is 'comment':
        fetched_ids = id_list
    cache_key = "cached_{source}_ids".format(source=source)#set cache key to top or new
    news_items,fetched_ids = fetch_items(fetched_ids,cache_key,source) #if source is not 'comment' else (fetched_ids,id_list)#fetch new items
    #print('Recent {source} item(s): {item}'.format(source=source, item = len(news_items)))
    fetched_ids = create_pk(news_items,fetched_ids,source)
    for item in news_items:#iterate and add other attributes present in item except id 
        item_id = item['id']    
        for key in item:   
          try:  
            if key is not 'id' and item['type'] not in ['unknown',None]:
                kwargs = {key:item[key]}
                Items.objects.filter(pk=item_id).update(**kwargs)
                if key == 'kids' and key not in [None,[]] and source not in ['comment','job']:
                    comment_list=item['kids']
                    comments=comments+comment_list[:2]
            else:    
                fetched_ids.remove(item_id)
                break
          except:
                pass               
    [query.save() for query in Items.objects.all()] #save all created objects
    print('Done with {}'.format(source))
    cache.set('trigger{}'.format(source),True)
    if source in ['top']:
        rearrange_db(fetched_ids)
        fetched_ids.reverse()      
    if source not in ['comment','job']:
        update_items('comment',comments)
    if source in ['job','comment']:
        return True         
       
    cache.delete(cache_key)
    cache.set(cache_key,fetched_ids) #set top or new to fetched in cache
    
    
    
    
    
    #A bug fix to walk around cache crashes
    # try:
    #     if cache.get('count'+source)>5:
    #         cache.delete('count'+source)
    #         cache.set('count'+source,5)
    #     else:
    #         cache.incr('count'+source)
    # except:
    #     cache.delete('count'+source)
    #     cache.set('count'+source,1)             

# def get_new_items():
#     print('Starting Task...')
#     fetched_ids = hacker_news.get_new_stories()
#     return fetch_items(fetched_ids,"cached_new_ids")
    

# def get_top_items():
#     print('Starting Task...')
#     fetched_ids = hacker_news.get_top_stories()
#     return fetch_items(fetched_ids,"cached_top_ids")
# create a lists

#front end uses the cache to fetch the ids from db
# init is when the cache is None    


#********************WHEN CACHE IS EMPTY**********************

# **Query for comments attached to the click of the comments button function
# first get selected item id
# load item from db with key kids to get a list of id's kids
# load all text of kids list in a list

# **Query for top items attached to button Top Items function
# filter ids with source top a list of dictionaries
# sort by date_fetched still a list of dictionaries

# **Query for new items attached to button Load of home function
# filter ids with source new a list of dictionaries     
# sort by date_fetched still a list of dictionaries

#*******************WHEN ITEM IN CACHE***********************
# **Query for top items attached to button Top Items function
# get cache value of top_items keys 
# based on cache values fetch ids to get thier items a list of dictionaries

# **Query for top items attached to button Top Items function
# get cache value of new_items keys 
# based on cache values fetch ids to get thier items a list of dictionaries
#ALL STORIES FOR THAT DAY WITH THE HIGHEST SCORES NEWS LETTER

#@celery.decorators.periodic_task(run_every=datetime.timedelta(minutes=5)) # here we assume we want it to be run every 5 mins

# from numpy import setdiff1d as diff 
# main_list =diff(list_2,list_1).tolist()

# set(list_2)-set(list_1)


#main_list = [b for a, b in zip(list1, list2) if a!= b] #this is much more efficient , since it's a single cheap pass over both lists with a single new list being constructed, no additional temporaries, no expensive containment checks.

# def changes(list_1,list_2):
#     changed=[]
#     if any(i != j for i, j in zip(list_1, list_2)):
#         boolean = [i == j for i, j in zip(list_1,list_2)]
#         for i in range(len(boolean)):
#              if not boolean[i]:
#                 elem = list_1[i]
#                 if elem in list_2:
#                     index_list_2 = list_2.index(elem)
#                     move = index_list_2-i
#                     changed.append((elem,move))
#                     print('{elem} changed postion from {i} to {index_y}'.format(elem=elem,i=i,index_y=index_list_2))
#                     print('{elem} moved {move} positions'.format(elem=elem,move=move))
#     return changed               
# def move_elements(list_,changes):
#     for tupl in changes:
#         item = tupl[0]
#         moves = tupl[1]
#         if item in list_:
#             old_index= list_.index(item)
#             new_index = old_index+moves
#             list_.insert(new_index, list_.pop(old_index))
#     return list_


# def get_hnapi_items():
#     print('Starting Task ...')
#     top_stories = hacker_news.get_top_stories()
#     selected_top_stories= top_stories[:100] #get first hundred top stories
#     cached_top_stories = cache.get("top stories object")
#     cached_top_news_items = cache.get("top items object")
#     db_objects = len(Items.objects.all())
#     db_ids = list(Items.objects.values_list('id',flat=True)) 
#     if  cached_top_stories is None:
#         selected_top_news_items= [hacker_news.get_item(story_id) for story_id in selected_top_stories]
#         cache.set("top stories object",selected_top_stories)
#         cache.set("top items object",selected_top_news_items)
#     else:
#         print(selected_top_stories)
#         selected_top_stories = list(set(cached_top_stories) ^ set(selected_top_stories))
#         print(selected_top_stories)
#         selected_top_news_items= [hacker_news.get_item(story_id) for story_id in selected_top_stories]
#         cache_top_stories_entry = selected_top_stories+cached_top_stories
#         cache_top_news_items_entry = selected_top_news_items + cached_top_news_items
#         cache.set("top stories object",cache_top_stories_entry)
#         cache.set("top items object",cache_top_news_items_entry)
#     #print(selected_top_news_items)    
#     return selected_top_news_items

#* when cache is empty and db not empty
#store fetched items to cache
#compare fetched with db_items instead
#store difference in cache too
#get all items presnt in db with attributes and put in cache
#* when db is empty
#initialized...store fetched items in both cache and db
# no need to compare items
# Store everything in cache with both id and items for new entries 
#* when cache is not empty
# compare cached items with fetched items
#if any(i != j for i, j in zip(x, y)): happens when there is no change