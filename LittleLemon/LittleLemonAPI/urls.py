from django.urls import path, include
from .views.menu_views import MenuViewSet
from .views.user_views import UsersView, SingleUserView
from .views.cart_views import CartView
from .views.order_views import OrderView, SingleOrderView
from .views.category_views import CategoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'category', CategoryViewSet)
router.register(r'menu-item', MenuViewSet, basename='menuitem')


urlpatterns = [
    path('', include(router.urls)),
    path('groups/<str:role>/users', UsersView.as_view(), name='group-list'),
    path('groups/<str:role>/users/<int:pk>', SingleUserView.as_view(), name='group-detail'),
    path('cart/menu-items', CartView.as_view()),
    path('orders', OrderView.as_view()),
    path('orders/<int:pk>', SingleOrderView.as_view()),
]