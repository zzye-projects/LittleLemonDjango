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
#### /api/category/{categoryId}
* Get: Gets the single category.
* Delete: Removes category.
* Put: Replaces category. Required payload field(s): slug, title.
* Patch: Updates category. Optional payload field(s): slug, title.

### Menu Item Endpoints
Get is available to any authenticated user. The other methods are only available to authenticated superusers/admin.
#### /api/menu-item
* Get: Gets list of all menu items.
* Post: Adds new menu item. Required payload field(s): title, price, featured (bool), category_id.
#### /api/menu-item/{menuItemId}
* Get: Gets the single menu-item.
* Delete: Removes category.
* Put: Replaces category. Required payload field(s): title, price, featured (bool), category_id.
* Patch: Updates category. Optional payload field(s): title, price, featured (bool), category_id.

### Cart Endpoints
Available to any authenticated customer user, NOT belonging to the manager nor the deliver crew group.
#### /api/cart/menu-item
* Get: Gets list of menu items within the cart of the user.
* Post: Adds the menu item to a new/existing cart of the user. Required payload field(s): menuitem_id. User can call this endpoint multiple times to increase the quantity of this item in the cart.
#### /api/cart/menu-item
* Delete: Clears the cart belonging to the user

### Order Endpoints
#### /api/orders
* Get: Gets list of orders. Managers get all orders, and customers and delivery crew only get orders that belong/assigned to them. List of orders can be filtered, ordered, and paginated.
* Post: Converts all cart items of the user into an order and empties their cart. Only users have access to this functionality
#### /api/orders/{orderId}
* * Get: Gets an order. Managers get all orders, and customers and delivery crew only get orders that belong/assigned to them.
* Delete: Deletes a specific order of the user.
* Put:
* Patch