from typing import Any

from rest_framework import mixins, viewsets
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from cafe.documents import ItemDocument
from cafe.models import Order, Item
from cafe.serializers import OrderSerializer, ItemSerializer, CalcRevenueSerializer
from cafe.services import filter_orders
from users.permissions import IsActive


@extend_schema_view(
    list=extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='table_number', required=False, type=int,
                             description='A list of table_numbers for filtering',
                             location=OpenApiParameter.QUERY, explode=True
                             ),
            OpenApiParameter(name='status', required=False, type=str,
                             description='A list of statuses for filtering',
                             location=OpenApiParameter.QUERY, explode=True
                             ),
            OpenApiParameter(name='date', required=False, type=OpenApiTypes.DATE,
                             description='A date for filtering',
                             location=OpenApiParameter.QUERY
                             ),
            OpenApiParameter(name='today', required=False, type=Any,
                             description='If today in query, returns list of today orders',
                             location=OpenApiParameter.QUERY
                             ),
        ],
        responses=OrderSerializer,
        methods=["GET"],
        description="Endpoint to get list of all orders"
    ),
    retrieve=extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this order',
                             location=OpenApiParameter.PATH)
        ],
        responses=OrderSerializer,
        methods=["GET"],
        description="Endpoint to get info about some order"
    ),
    create=extend_schema(
        request=OrderSerializer,
        parameters=None,
        responses=OrderSerializer,
        methods=["POST"],
        description="Endpoint to create order"
    ),
    update=extend_schema(
        request=OrderSerializer,
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this order',
                             location=OpenApiParameter.PATH)
        ],
        responses=OrderSerializer,
        methods=["PUT"],
        description="Endpoint to full change some order info"
    ),
    partial_update=extend_schema(
        request=OrderSerializer,
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this order',
                             location=OpenApiParameter.PATH)
        ],
        responses=OrderSerializer,
        methods=["PATCH"],
        description="Endpoint to partial change some order info"
    )
)
class OrdersViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related('items').filter().order_by('-created')
    permission_classes = [IsAdminUser, IsActive]

    def list(self, request, *args, **kwargs):
        query = request.query_params
        queryset = filter_orders(self.get_queryset(), query)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        request=None,
        parameters=None,
        responses=ItemSerializer,
        methods=["GET"],
        description="Endpoint to get list of all items"
    ),
    retrieve=extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this item',
                             location=OpenApiParameter.PATH)
        ],
        responses=ItemSerializer,
        methods=["GET"],
        description="Endpoint to get info about some item"
    ),
    create=extend_schema(
        request=ItemSerializer,
        parameters=None,
        responses=ItemSerializer,
        methods=["POST"],
        description="Endpoint to create item"
    ),
    update=extend_schema(
        request=ItemSerializer,
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this item',
                             location=OpenApiParameter.PATH)
        ],
        responses=ItemSerializer,
        methods=["PUT"],
        description="Endpoint to full change some item info"
    ),
    partial_update=extend_schema(
        request=ItemSerializer,
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this item',
                             location=OpenApiParameter.PATH)
        ],
        responses=ItemSerializer,
        methods=["PATCH"],
        description="Endpoint to partial change some item info"
    )
)
class ItemsViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.filter().order_by('id')
    permission_classes = [IsAdminUser, IsActive]


@extend_schema_view(
    create=extend_schema(
        request=CalcRevenueSerializer,
        parameters=None,
        responses={200: int},
        methods=["POST"],
        description="Endpoint to calc revenue for some date"
    )
)
class CalcRevenueView(CreateAPIView):
    serializer_class = CalcRevenueSerializer
    permission_classes = [IsAdminUser, IsActive]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        revenue = serializer.save()
        return Response({'revenue': revenue}, status=HTTP_200_OK)


@extend_schema_view(
    retrieve=extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='match', required=True, type=str,
                             description='A match phrase',
                             location=OpenApiParameter.QUERY, explode=False
                             ),
        ],
        responses=ItemSerializer,
        methods=["GET"],
        description="Endpoint to elastic search items"
    )
)
class SearchItemView(RetrieveAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUser, IsActive]

    def retrieve(self, request, *args, **kwargs):
        search_results = ItemDocument.search().query(
            "multi_match",
            query=request.query_params.get('match'),
            fields=["name", "description"]
        ).execute()
        if search_results:
            serializer = self.get_serializer(get_object_or_404(Item, pk=search_results[0].meta['id']))
            return Response(serializer.data)
        return Response({'detail': "Объектов не обнаружено"}, status=HTTP_400_BAD_REQUEST)
