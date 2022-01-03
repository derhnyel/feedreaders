[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/derhnyel/feedreaders)<h3 align="center">FeedReaders</h1>
<hr/>

### STARTING UP PROJECT
- Get python installed.

- Check python version
###### In the project directory, you can run:
###### `python--version" : "check python version"`,

- Set up Postgresql Server on your Computer and Get the service Running.
 
- Create a database with the name hackernewsdb.

- Connect to the Postgres database.

- A Virtual Machine was shipped with this project Activate it with  on Windows with,
###### `path_to_project_directory/hackernews/news/Scripts/activate.bat` 
###### "Start virtual machine on windows"

- Or create a virtual environment 
###### `pip install venv` 
"Install virtualmachine package"
Navigate to your desired virtual environment path and run command
###### `venv nameofvirtualenv`
###### "Create new virtual machine"

- Navigate into the project directory via terminal (newsaggregator directory should be your root directory).

- If you created a new virtual machine run command 
###### `pip install -r requirements.txt`
###### "Required libaries installed"
###### This will install the the neccesarry libaries needed to run the application on your machine. 

- Run make Migrations on hackernews_engine app using command 
###### `python manage.py makemigations`

- Run Migrations with command 
###### `python manage.py migrate`

- Start server 
###### `python manage.py runserver" : "python-scripts start"`,
The app is built using `Django` so this command Runs the app in Development mode. Open [http://localhost:8000](http://localhost:8000) to view it in the browser. The page will reload if you make edits. 
To turn this feature off use the --noreload 
###### `python manage.py runserver --noreload`
###### "Python-script starts with noreload"
###### You will also see any lint errors in the console.

- You can hover over items on the webpage to view thier text.

- The default home page is the New stories page.

#### NOTE
    At first, running the page takes a while(around 2minutes) to load since the database is empty and has to be populated.
    Also comments are fetched and stored in the database after all other tasks are done , so it might take a while for it to appear on the webpage.
    After the initialization all these do not happen, the page loads normally with all resources available on it. 
    I would advice aganst using the django default sql database because it has lock that makes it process one request at a time thierby preventing concurrent requests.   

### MAKING API REQUESTS

#### Responses

Many API endpoints return the JSON representation of the resources created or edited. However, if an invalid request is submitted, or some other error occurs, Feedreaders returns a JSON response in the following format:

```javascript
{
  "error" : string,
  "success" : bool,
  "result"    : string
}
```

The `error` attribute contains a message commonly used to indicate errors or, in the case of deleting a resource, success that the resource was properly deleted.

The `success` attribute describes if the transaction was successful or not.

The `result` attribute contains any other metadata associated with the response. This will be an escaped string containing JSON data.

#### Status Codes

Feedreaders returns the following status codes in its API:

| Status Code | Description |
| :--- | :--- |
| 200 | `OK` |
| 201 | `CREATED` |
| 400 | `BAD REQUEST` |
| 404 | `NOT FOUND` |
| 500 | `INTERNAL SERVER ERROR` |

#### Links

- [Repo](https://github.com/derhnyel/feedreaders "feedreaders Repo")

- [Live](https://feedreaders.herokuapp.com "Live View")


#### API CallS

- Interact with the rest_api from browser using [http://localhost:8000/api](http://localhost:8000/api)
- **GET** 
Query the Api  [http://localhost:8000/api](http://localhost:8000/api) with a `GET` request which returns all the items in the database.
- **GET?FILTER= (fiter_param)**   
You can also query the Api [http://localhost:8000/api?filter=item_type](http://localhost:8000/api/filter=item_type) <restricted to story,comment,job> with a `GET` request and a filter based on the item's type to return only items with that type.
- **GET<PK> (PRIMARY KEY)** 
Query the Api [http://localhost:8000/api/<pk>](http://localhost:8000/api/<pk>) with a `GET` request with primary key in the url and it returns the record with that primarykey and its attributes.
- **POST (CREATE)** 
Query the Api  [http://localhost:8000/api](http://localhost:8000/api) with a `POST` request and payload with 
`{ title:"your_title",url:"your_url",text:"your_text"}` to create a new item a primary key is automatically generated.
- **UPDATE**
Query the Api [http://localhost:8000/api/<pk>](http://localhost:8000/api/<pk>) with a `PUT` request with the primary key in the url and a payload `{ title:"your_title",url:"your_url",text:"your_text"}` to modify that particular record.
- **DELETE**
Query the Api [http://localhost:8000/api/<pk>](http://localhost:8000/api/<pk>) with a `DELETE` request with the primary key in the url to delete a record from the database.

#### NOTE 
    The API Requests `PUT`,`UPDATE`,`DELETE` only works for items created using the API.




### Screenshots

![Home Page](/screenshots/1.png "Home Page")


Give a ⭐️ if you like this project!