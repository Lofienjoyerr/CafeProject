from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser

from cafe.models import Order, Item
from cafe.serializers import OrderSerializer, ItemSerializer, CalcRevenueSerializer
from users.permissions import IsActive


class OrdersViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.filter().order_by('-created')
    permission_classes = [IsAdminUser, IsActive]

    def get_queryset(self):
        if self.action == "list":  # noqa
            query = self.request.query_params
            queryset = self.queryset
            if 'table_number' in query:
                queryset = queryset.filter(table_number__in=[int(table) for table in query.getlist('table_number')])
            if 'status' in query:
                queryset = queryset.filter(status__in=query.getlist('status'))
            if 'date' in query:
                queryset = queryset.filter(created__date=query.get('date'))
            if 'today' in query:
                now = timezone.now()
                queryset = queryset.filter(created__day=now.day)
            return queryset
        return self.queryset


class ItemsViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.filter().order_by('-id')
    permission_classes = [IsAdminUser, IsActive]


class CalcRevenueView(CreateAPIView):
    serializer_class = CalcRevenueSerializer
    permission_classes = [IsAdminUser, IsActive]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        revenue = serializer.save()
        return Response({'revenue': revenue}, status=HTTP_200_OK)
