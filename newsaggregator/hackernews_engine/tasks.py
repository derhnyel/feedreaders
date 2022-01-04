from .utils import  hnapi
from django.core.cache import cache
from .models import Items
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler




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

def fetch_items(fetched_ids,cache_key,source,db_ids):
    """Perform checks and Fetch ids and items from Api"""
    print('Fetched ids {source} : {ids}'.format(source=source,ids=len(fetched_ids) if fetched_ids is not None else None ))    
    cached_ids = cache.get(cache_key) #get cached ids
    print('Cached ids {source} : {ids}'.format(source=source,ids=len(cached_ids) if cached_ids is not None else None ))

   

    if cached_ids is None and db_ids.exists(): #web app restarted and Database has objects or a cache hot reload
        new_ids=disimilar_elements(db_ids,fetched_ids)#get ids in fetched_ids that are not in database_ids
        #new_ids = purge_similar_items(new_ids,db_ids,source)
        new_items= [hacker_news.get_item(_id) for _id in new_ids]# get item list by id from api 
        #cache.set('count'+source,1) #set count to 1    
        return new_items,fetched_ids
    
    elif not db_ids.exists() and cached_ids is None: #At first Start .. Initialization of db
        items = [hacker_news.get_item(_id) for _id in fetched_ids] #fetch items using fetched ids from api
        return items,fetched_ids
    
    elif cached_ids is not None: #cache contains previous fetched results
        new_ids = disimilar_elements(cached_ids,fetched_ids)#find new ids in fetched ids not in cached ids
        new_ids = purge_similar_items(new_ids,db_ids,source) #remove items added to database in the past from cache
        new_items = [hacker_news.get_item(_id) for _id in new_ids] #get items
        return new_items,fetched_ids   


def create_pk(new_items,fetched_ids,source):
    """Create model object instance for all new ids as primary key"""
    for item in  new_items:
      try:
        if item['type'] != 'unknown' and item['type'] != None:
            if source != 'comment':
                if source == 'top':
                    Items.objects.create(id=item['id'],top=True)
                if source in ['job','new']:
                    Items.objects.create(id=item['id'],source=source)        
            else:
                Items.objects.create(id=item['id'],source=source,parent=item['parent'])
        else:
            fetched_ids.remove(item['id'])            
      except Exception as e:
          pass
    return fetched_ids 


def rearrange_db(_list):
    try:
        for id in _list.reverse():
            Items.objects.filter(pk=id).update(date_fetched=datetime.now(),top=True)
    except:pass        
    

def update_items(source,id_list=None):
    """Save items to database"""
    print('Starting task to fetch and store {source} items...'.format(source=source))
    db_ids = Items.objects.values_list('id',flat=True) # get database ids
    print('Stored Database IDS {source} : {ids} '.format(source=source, ids=len(db_ids)))
    #get top or new stories
    comments=[]
    if len(db_ids)<800:
        slice_idx=100
    elif len(db_ids)>800 and len(db_ids)<1500:
        slice_idx=200
    elif len(db_ids)>1500 and len(db_ids)<2200:
        slice_idx=300
    elif len(db_ids)>2200 and len(db_ids)<3000:
        slice_idx=400
    else:
        slice_idx=500
        
    if source is 'top':
        fetched_ids = hacker_news.get_top_stories()[:slice_idx] 
    elif source is 'new':
        fetched_ids=hacker_news.get_new_stories()[:slice_idx] 
    elif source is 'job':
        fetched_ids= hacker_news.get_jobs()
    elif source is 'comment':
        fetched_ids = id_list
    cache_key = "cached_{source}_ids".format(source=source)#set cache key to top or new
    news_items,fetched_ids = fetch_items(fetched_ids,cache_key,source,db_ids) #if source is not 'comment' else (fetched_ids,id_list)#fetch new items
    #print('Recent {source} item(s): {item}'.format(source=source, item = len(news_items)))
    fetched_ids = create_pk(news_items,fetched_ids,source)
    for item in news_items:#iterate and add other attributes present in item except id 
        item_id = item['id']    
        for key in item:   
          try:  
            if key is not 'id' and item['type'] not in ['unknown',None]:
                if key == 'kids' and key not in [None,[]] and source not in ['comment','job']:
                    comment_list=item['kids']
                    comments = comments+comment_list[:10] if len(comment_list) > 10 else comments+comment_list                    
                    kwargs = {key:len(item[key])}
                    Items.objects.filter(pk=item_id).update(**kwargs)
                if key != 'kids' and key != 'parts':
                    kwargs = {key:item[key]}
                    Items.objects.filter(pk=item_id).update(**kwargs)
            elif  key != 'id' and item['type'] in ['unknown',None]:    
                fetched_ids.remove(item_id)
                invalid_obj = Items.objects.get(pk=item_id)
                invalid_obj.delete()
                break
          except:
                pass               
    [query.save() for query in Items.objects.all()] #save all created objects
    if source in ['job','comment']:
        return True 
    if source in ['top']:
        rearrange_db(fetched_ids)
        [query.save() for query in Items.objects.all()]
        fetched_ids.reverse()
    if source in ['top','new']:    
        cache.delete(cache_key)
        cache.set(cache_key,fetched_ids) #set top or new to fetched in cache     
    if comments!=[]:         
        scheduler= BackgroundScheduler(timezone="Asia/Beirut")
        scheduler.add_job(update_items,args=['comment',comments],run_date=datetime.now(),id="FetchCommentsTaskid",misfire_grace_time=None,replace_existing=False)
        scheduler.start()
        
        

    
    