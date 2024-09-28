from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .globals import *

class IsManagerAdminOrGET(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied(detail='Only authenticated users can perform this action')
        elif request.method == 'GET' or user.is_superuser or \
            user.groups.filter(id=ROLESLUG_ROLE['manager']).exists():
            return True
        raise PermissionDenied(detail='Only managers and superusers can perform this action')

class IsManagerAdminOr403(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and (
            user.groups.filter(id=ROLESLUG_ROLE['manager']).exists() or user.is_staff):
            return True
        raise PermissionDenied(detail='Only managers and admin staff can perform this action')
    
class IsCustomerOr403(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.groups.filter(id=ROLESLUG_ROLE['manager']).exists() or \
            request.user.groups.filter(id=ROLESLUG_ROLE['delivery-crew']).exists():
            raise PermissionDenied(detail='Only customers can perform this action')
        return True

class SingleOrderPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and (
            (not request.user.groups.first() and request.method=='GET') or # Customer
            (request.user.groups.filter(id=ROLESLUG_ROLE['manager']).exists() or #Manager
            (request.method in ('GET','PATCH') and # Delivery-crew
            request.user.groups.filter(id=ROLESLUG_ROLE['delivery-crew']).exists()))):
            return True
        raise PermissionDenied(detail='You are not authorised to perform this action')

class IsCustomerOrGET(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and (request.method == 'GET' or
            not request.user.groups.first()):
            return True
        raise PermissionDenied(detail='You are not authorised to perform this action')

