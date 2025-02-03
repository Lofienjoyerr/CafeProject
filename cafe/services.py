from datetime import datetime

from django.utils import timezone
from django.http import QueryDict
from django.db.models import QuerySet


def filter_by_table_number(queryset: QuerySet, query: QueryDict) -> QuerySet:
    lst = query.getlist('table_number')
    queryset = queryset.filter(table_number__in=[int(table) for table in lst])
    return queryset


def filter_by_status(queryset: QuerySet, query: QueryDict) -> QuerySet:
    lst = query.getlist('status')
    queryset = queryset.filter(status__in=lst)
    return queryset


def filter_by_date(queryset: QuerySet, query: QueryDict) -> QuerySet:
    date = query.get('date')
    queryset = queryset.filter(created__date=date)
    return queryset


def filter_by_today(queryset: QuerySet, now: datetime) -> QuerySet:
    queryset = queryset.filter(created__year=now.year, created__month=now.month, created__day=now.day)
    return queryset


def filter_orders(queryset: QuerySet, query: QueryDict) -> QuerySet:
    if 'table_number' in query:
        queryset = filter_by_table_number(queryset, query)
    if 'status' in query:
        queryset = filter_by_status(queryset, query)
    if 'date' in query:
        queryset = filter_by_date(queryset, query)
    if 'today' in query:
        queryset = filter_by_today(queryset, timezone.localtime(timezone.now()))
    return queryset
