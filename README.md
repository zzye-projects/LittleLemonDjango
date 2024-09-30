# LittleLemonDjango

Setup Details
========================
<ol>
    <li> Navigate into the project folder </li>
</ol>
- Update Settings.py > DATABASES based on your database configs
- pipenv shell
- pipenv install
- Ensure that you mysql/other db server has been started
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver
9. Create a superuser
10. Create groups "Manager" and "Delivery Crew" through the admin panel as a superuser

Available Endpoints
========================
/auth/ djoser paths
/api/groups/manager/users
/api/groups/delivery-crew/users

