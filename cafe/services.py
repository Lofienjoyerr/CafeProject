from datetime import datetime

from django.core.cache import cache
from django.utils import timezone
from django.http import QueryDict
from django.db.models import QuerySet

from cafe.models import Order


def filter_by_table_number(queryset: QuerySet, query: QueryDict) -> QuerySet:
    lst = [table for table in query.getlist('table_number')]
    key = f"orders:table_number:{"-".join(lst)}"
    target_queryset = cache.get(key)
    if not target_queryset:
        target_queryset = Order.objects.filter(table_number__in=[int(table) for table in lst])
        cache.set(key, target_queryset)
    return queryset.intersection(target_queryset)


def filter_by_status(queryset: QuerySet, query: QueryDict) -> QuerySet:
    lst = query.getlist('status')
    key = f"orders:status:{"-".join(lst)}"
    target_queryset = cache.get(key)
    if not target_queryset:
        target_queryset = Order.objects.filter(status__in=lst)
        cache.set(key, target_queryset)
    return queryset.intersection(target_queryset)


def filter_by_date(queryset: QuerySet, query: QueryDict) -> QuerySet:
    date = query.get('date')
    key = f"orders:date:{date}"
    target_queryset = cache.get(key)
    if not target_queryset:
        target_queryset = Order.objects.filter(created__date=date)
        cache.set(key, target_queryset)
    return queryset.intersection(target_queryset)


def filter_by_today(queryset: QuerySet, now: datetime) -> QuerySet:
    key = f"orders:today:{now}"
    target_queryset = cache.get(key)
    if not target_queryset:
        target_queryset = Order.objects.filter(created__year=now.year, created__month=now.month, created__day=now.day)
        cache.set(key, target_queryset)
    return queryset.intersection(target_queryset)


def filter_orders(queryset: QuerySet, query: QueryDict) -> QuerySet:
    if 'table_number' in query:
        queryset = filter_by_table_number(queryset, query)
    if 'status' in query:
        queryset = filter_by_status(queryset, query)
    if 'date' in query:
        queryset = filter_by_date(queryset, query)
    if 'today' in query:
        queryset = filter_by_today(queryset, timezone.localtime(timezone.now()))
    return queryset.order_by('-created')
