# LittleLemonDjango

## Setup Details
* Navigate into the project folder
* Update Settings.py > DATABASES based on your database configs
* pipenv shell
* pipenv install
* Ensure that you mysql/other db server has been started
* python manage.py makemigrations
* python manage.py migrate
* python manage.py runserver
* Create a superuser
* Create groups "Manager" and "Delivery Crew" through the admin panel as a superuser

## Available Endpoints

### Djoser User Management Endpoints
* /auth/ - See https://djoser.readthedocs.io/en/latest/base_endpoints.html

### User/api/groups/manager/users
* Auth: Only available to authenticated superusers/admin
* Get: Gets list of all manager users
* Post: Adds user to manager group. Required a valid 'username' in payload
### /api/groups/manager/users/{userId}
* Auth: Only available to authenticated superusers/admin
* Delete: Removes user from the manager group

### /api/groups/delivery-crew/users
* Auth: Only available to authenticated superusers/admin/managers
* Get: Gets list of all delivery crew users
* Post: Adds user to delivery crew group. Required a valid 'username' in payload
### /api/groups/manager/users/{userId}
* Auth: Only available to authenticated superusers/admin/managers
* Delete: Removes user from the delivery crew group

