# LittleLemonDjango
## Description
TBD

## Setup Details
* Navigate into the project folder
* Update Settings.py > DATABASES based on your database configs
* pipenv shell
* pipenv install
* Ensure that you mysql/other db server has been started
* python manage.py makemigrations
* python manage.py migrate
* python manage.py runserver
* python manage.py createsuperuser
* Create groups "Manager" and "Delivery Crew" through the admin panel as a superuser

## Available Endpoints

### Djoser User Management Endpoints
* /auth/ - See https://djoser.readthedocs.io/en/latest/base_endpoints.html

### User Group Endpoints
#### User/api/groups/manager/users
Only available to authenticated superusers/admin.
* Get: Gets list of all manager users.
* Post: Adds user to manager group. Required payload field(s): username.
#### /api/groups/manager/users/{userId}
* Auth: Only available to authenticated superusers/admin.
* Delete: Removes user from the manager group.

#### /api/groups/delivery-crew/users
Only available to authenticated superusers/admin/managers.
* Get: Gets list of all delivery crew users.
* Post: Adds user to delivery crew group. Required payload field(s): username.
#### /api/groups/delivery-crew/users/{userId}
* Delete: Removes user from the delivery crew group.

### Category Endpoints
Get is available to any authenticated user. The other methods are only available to authenticated superusers/admin.
#### User/api/category
* Get: Gets list of all categories.
* Post: Adds new category. Required payload field(s): slug, title.
#### /api/category{categoryId}
* Delete: Removes category.
* Put: Replaces category. Required payload field(s): slug, title.
* Patch: Updates category. Optional payload field(s): slug, title.

### Menu Item Endpoints
Get is available to any authenticated user. The other methods are only available to authenticated superusers/admin.
#### /api/menu-item
* Get: Gets list of all menu items.
* Post: Adds new menu item. Required payload field(s): title, price, featured (bool), category_id.
#### /api/menu-item{categoryId}
* Delete: Removes category.
* Put: Replaces category. Required payload field(s): title, price, featured (bool), category_id.
* Patch: Updates category. Optional payload field(s): title, price, featured (bool), category_id.

### Cart Endpoints
Get is available to any authenticated customer user, NOT belonging to the manager nor the deliver crew group.
#### /api/cart/menu-item
* Get: Gets list of menu items within the cart of the user.
* Post: Adds the menu item to a new/existing cart of the user. Required payload field(s): menuitem. User can call this endpoint multiple times to increase the quantity of this item in the cart.
#### /api/cart/menu-item
* Delete: Clears the cart belonging to the user