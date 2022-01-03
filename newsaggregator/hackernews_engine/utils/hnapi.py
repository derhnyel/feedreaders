#fetch news articles from hackernew api
from datetime import datetime
import requests
import time
# from fake_useragent import UserAgent


class Item():
    """Set attributes(keyword arguments) of Item automatically"""
    def __init__(self, **entries):
        self.__dict__.update(entries)


class User():
    """Set attributes(keyword arguments) of User automatically"""
    def __init__(self, **entries):
        self.__dict__.update(entries)


class hackernews_engine():
    """Engine for accessing hackernews api and making various allowed api requests"""
    
    def __init__(self, timeout=None):
        """Initialize hackernews engine class with hackernews api url and timeout for processing api call"""
        self.url = 'https://hacker-news.firebaseio.com/v0/{url}'
        self.timeout = 5 if timeout is None else timeout  
    def request(self, method, url):
        """Function to send POST AND GET request to API and return API's response """
        time.sleep(0.01) #prevents api from flagging request as DDos attack
        url = self.url.format(url=url) #format url path 
        response=self.handle_exceptions(requests.request(method, url, timeout=self.timeout))
        return  response#return api response

    def get_item(self, item_unique_id):
        """Function to Get Item By ID"""
        url = 'item/{item_unique_id}.json'.format(item_unique_id=item_unique_id)
        api_response = self.request('GET', url) 
        if api_response is not None:
            item = api_response.json() 
        else:
            return None
        #print('item: {} \nid: {}'.format(item,item_unique_id))    
        try:
            if 'time' in item: #check if time is present in response
                item['time'] = datetime.fromtimestamp(item['time']) #format items timestamp with datetime
            return item
        except:
            return({'id':item_unique_id,'time':datetime.now(),type:'unknown'})
              
        #return Item(**item)


    def get_user(self, user_id):
        """Function to Get User By ID"""
        url = 'user/{user_id}.json'.format(user_id=user_id)
        api_response = self.request('GET', url)
        if api_response is not None:
           user = api_response.json() 
        else:
            return None
        user['created'] = datetime.fromtimestamp(user['created'])# format date user was created with datetime
        return User(**user) #return initialized User Class with the api response(user) as keyword arguments

    def get_top_stories(self):
        """Function to get Top stories"""
        api_response = self.request('GET', 'topstories.json')
        if api_response is not None:
           stories = api_response.json() 
        else:
            return None
        return stories
    def get_new_stories(self):
        """Function to get New stories"""
        api_response = self.request('GET', 'newstories.json')
        if api_response is not None:
           stories = api_response.json() 
        else:
            return None
        return stories

  

    def get_max_item(self):
        """Function to get max_item """
        api_response = self.request('GET', 'maxitem.json')
        if api_response is not None:
           max_item = api_response.json() 
        else:
            return None
        return max_item

    def get_updates(self):
        """Function to get recent updates and changes"""
        api_response = self.request('GET', 'updates.json')
        if api_response is not None:
           update = api_response.json() 
        else:
            return None
        return update

    def handle_exceptions(self,request):
        try:
            request.raise_for_status()
            return request
        except:
             return None  
    def get_jobs(self): 
        api_response = self.request('GET', 'jobstories.json')
        if api_response is not None:
           jobs= api_response.json() 
        else:
            return None
        return jobs         
 








