from django.urls import path, include
from .views.menu_views import MenuItemsView, SingleMenuItemView
from .views.user_views import UsersView, SingleUserView
from .views.cart_views import CartView
from .views.order_views import OrderView, SingleOrderView
from .views.category_views import CategoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'category', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('menu-items', MenuItemsView.as_view()),
    path('menu-items/<int:pk>', SingleMenuItemView.as_view()),
    path('groups/<str:role>/users', UsersView.as_view()),
    path('groups/<str:role>/users/<int:pk>', SingleUserView.as_view()),
    path('cart/menu-items', CartView.as_view()),
    path('orders', OrderView.as_view()),
    path('orders/<int:pk>', SingleOrderView.as_view()),
]