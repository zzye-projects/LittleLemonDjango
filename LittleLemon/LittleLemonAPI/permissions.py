from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

class IsManagerAdminOrGET(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            raise AuthenticationFailed(detail='Only authenticated users can perform this action')
        elif request.method == 'GET' or user.is_superuser or \
            user.groups.filter(name='Manager').exists():
            return True
        raise PermissionDenied(detail='Only managers and superusers can perform this action')

class IsManagerAdminOr403(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and \
            (user.is_superuser or \
            (view.kwargs.get('role') == 'delivery-crew' and \
            user.groups.filter(name='Manager').exists())):
                return True
        raise PermissionDenied(detail='You are not authorised to perform this action')
    
class IsCustomerOr403(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.is_superuser or \
            request.user.groups.filter(name='Manager').exists() or \
            request.user.groups.filter(name='Delivery Crew').exists():
            raise PermissionDenied(detail='Only customers can perform this action')
        return True

class IsCustomerOrGET(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and (request.method == 'GET' or
            not request.user.groups.first()):
            return True
        raise PermissionDenied(detail='You are not authorised to perform this action')

class SingleOrderPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and (
            (not request.user.groups.first() and request.method=='GET') or # Customer
            (request.user.groups.filter(name='Manager').exists() or #Manager
            (request.method in ('GET','PATCH') and # Delivery-crew
            request.user.groups.filter(name='Delivery Crew').exists()))):
            return True
        raise PermissionDenied(detail='You are not authorised to perform this action')



