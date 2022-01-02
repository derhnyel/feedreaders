*********STARTING UP PROJECT********

 1. Set up Postgresql Server on your Computer ad Get the service Running.
 2. Create a database with the name hackernewsdb.
 3. Connect to the Postgres database.
 4. I shipped a Virtual Machine with this project Activate it or create a new one with command "path_to_project_directory/hackernews/news/Scripts/activate.bat" on Windows.
 5. If you dont want to use the virtual machine run command "pip install -r requirements.txt".
 6. Navigate into the project directory via terminal (newsaggregator directory should be your root directory).
 7. Run make Migrations on hackernews_engine app using command "python manage.py makemigations hackernews_engine"
 8. Run Migrations with command "python manage.py migrate".
 9. Start server with command "python manage.py runserver --noreload"
 10. Enter https://127.0.0.1:8000 to access webpage. Navigate through the buttons on the page.
 11. You can hover over items to view thier text.
 12. The default home page is the New items.

 Note:
    At first, running the page takes a while(<=2minutes) to load since the database is empty and has to be populated.
    Also comments are fetched and stored in the database after all other tasks are done , so it might take a while for it to appear on the webpage.
    After the initialization all these do not happen, the page loads normally with all resources available on it. 
    I would advice aganst using the django default sql database because it has lock that makes it process one request at a time thierby preventing concurrent requests.   


**********MAKING API CALLS***********

Interact with the rest_api from browser using (https://127.0.0.1:8000/api/).

### GET ###   Query the Api  (https://127.0.0.1:8000/api/) with a get request which returns all the items in the database.
### GET FILTER ###   You can also query the Api (https://127.0.0.1:8000/?filter=item_type)[restricted to story,comment,job] with a get request and a filter baseed on the item's type to return only items with that type.
### GET PRIMARY KEY ### Query the Api  (https://127.0.0.1:8000/api/<pk>) with a get request with primary key in the url and it returns the record with that primarykey and its attributes.
### POST (CREATE) ### Query the Api (https://127.0.0.1:8000/api/) with a post request and payload with {"title":your_title,"url":your_url,"text"::your_text} to create a new item a primary key is automatically generated.
### UPDATE ### Query the Api (https://127.0.0.1:8000/api/<pk>) with a put request with the primary key in the url and a payload {"title":your_title,"url":your_url,"text":your_text} to modify that particular record.
### DELETE ### Query the Api (https://127.0.0.1:8000/api/<pk>) with a delete request with the primary key in the url to delete a record from the database.

Note: 
    The Api PUT,UPDATE,DELETE only works for items created using the api.







