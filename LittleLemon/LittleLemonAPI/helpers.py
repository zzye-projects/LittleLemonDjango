from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination


def get_filtered_items(items, request, filter_params):
    for param, filter_param in filter_params.items():
        filter_value = request.query_params.get(param)
        filter_by = {filter_param: filter_value}
        if filter_value: items = items.filter(**filter_by)
    return items

def get_paginated_items(items, request):
    page = request.query_params.get('page', default=1)
    perpage = request.query_params.get('perpage', default=100)

    paginator = Paginator(items, per_page=perpage)
    items = paginator.page(number=page)
    return items

class CustomPageSize(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100