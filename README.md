# django-template
Basic Django template to get start a project


#### Create a Python pipenv Environment
Follow instruction https://docs.pipenv.org/ for installing pipenv.

#### To activate pipenv environment try following:
`pipenv shell`

#### To deactiavte pipenv environment 
exit

#### After activating pipenv environment install required dependencies by following command:  
`pip install -r requirements.txt`

Change the `.env.example` file to `.env` and add required details 

#### To create superuser
`python manage.py createsuperuser`

#### To run the project
`python manage.py runserver` 

### To install redis-server

https://gist.github.com/tomysmile/1b8a321e7c58499ef9f9441b2faa0aa8

To Run Background process in our project needs to activate `redis`, `celery worker`, `celery beat` services in three separate `Terminals`

COMMANDS TO RUN inside our project directory with activation of virtual environment

1) `redis-server` to activate redis # for Queuing Tasks
2) `celery worker -A project_name --loglevel=debug --concurrency=4` to actiave celery beat    
3) `celery -A project_name beat` to activate celery beat    
4) `celery -A project_name beat -l INFO` to activate celery beat scheduler
