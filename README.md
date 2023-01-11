#### Running Tests in Development 

### How do I get set up? ###

* Unzip the file.

* Make sure you have python3 installed in your machine.

* Install virtualenv on your system. For linux: ```pip install virtualenv```.

* Go to restaurant-voting dir. And create virtual environment with virtualenv: ```virtualenv -p /usr/bin/python3 .env```.

* Activate the virtual environment: source ```.env/bin/activate```.

* Install required dependencies: ```pip install -r requirements.txt```.

* Set these environment variables which is forwarded via email with corresponding values.

* Go to website dir where the manage.py file.
    * in manage.py 
        * Uncomment 'DJANGO_SETTINGS_MODULE' to website.dev for testing the application in local server and comment 'website.production'.
        * Uncomment 'DJANGO_SETTINGS_MODULE' to website.production for production and comment 'website.dev'

* Create migrations files: ```./manage.py makemigrations```.

* Update the database with migrations: ```./manage.py migrate```.

* Start the local server: ```./manage.py runserver```.

**.Environent Variable **
```
    SECRET_KEY=foo
```