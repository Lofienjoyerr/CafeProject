from typing import Type

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, CreateAPIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, OpenApiRequest, OpenApiParameter, \
    inline_serializer

from core.settings import EMAIL_CONFIRM_TIME
from .permissions import IsOwnerOrIsAdmin, IsEmailOwnerOrIsAdmin, IsActive
from .serializers import (AdminUsersListSerializer, UsersListSerializer,
                          AdminUserDetailSerializer, UserDetailSerializer, PasswordChangeSerializer, RegisterSerializer,
                          EmailChangeSerializer, PasswordResetSerializer, PasswordResetVerifySerializer,
                          EmailResendSerializer, PasswordResendSerializer, MyTokenObtainPairSerializer)
from .services import get_user, verify_email, get_password_reset_token, create_email_and_token, get_email_address, \
    get_email_address_active_tokens, get_user_by_email, get_password_active_tokens
from users.tasks import send_email_verify, send_password_reset

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        request=None,
        parameters=None,
        responses={
            HTTP_200_OK: OpenApiResponse(
                description='Success',
                response={
                    'application/json': [UsersListSerializer, AdminUsersListSerializer]
                }
            )
        },
        methods=["GET"],
        description="Endpoint to get list of all users"
    )
)
class UsersView(ListAPIView):
    queryset = User.objects.all().order_by("date_joined")

    def get_serializer_class(self, *args, **kwargs) -> Type[AdminUsersListSerializer | UsersListSerializer]:
        if self.request.user.is_active and self.request.user.email_address.verified and (
                self.request.user.is_staff or self.request.user.is_superuser):
            return AdminUsersListSerializer
        return UsersListSerializer


@extend_schema_view(
    retrieve=extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this user',
                             location=OpenApiParameter.PATH)
        ],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description='Success',
                response={
                    'application/json': [UserDetailSerializer, AdminUserDetailSerializer]
                }
            )
        },
        methods=["GET"],
        description="Endpoint to get info about some user"
    ),
    update=extend_schema(
        request=OpenApiRequest(
            request=[UserDetailSerializer, AdminUserDetailSerializer]
        ),
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this user',
                             location=OpenApiParameter.PATH)
        ],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description='Success',
                response={
                    'application/json': [UserDetailSerializer, AdminUserDetailSerializer]
                }
            )
        },
        methods=["PUT"],
        description="Endpoint to full change some user info"
    ),
    partial_update=extend_schema(
        request=OpenApiRequest(
            request=[UserDetailSerializer, AdminUserDetailSerializer]
        ),
        parameters=[
            OpenApiParameter(name='id', required=True, type=int,
                             description='A unique integer value identifying this user',
                             location=OpenApiParameter.PATH)
        ],
        responses={
            HTTP_200_OK: OpenApiResponse(
                description='Success',
                response={
                    'application/json': [UserDetailSerializer, AdminUserDetailSerializer]
                }
            )
        },
        methods=["PATCH"],
        description="Endpoint to partial change some user info"
    )
)
class UserDetailView(RetrieveUpdateAPIView):
    queryset = User.objects.all().order_by("date_joined")
    permission_classes = [IsActive, IsOwnerOrIsAdmin]

    def get_serializer_class(self, *args, **kwargs) -> Type[AdminUserDetailSerializer | UserDetailSerializer]:
        if self.request.user.is_active and self.request.user.email_address.verified and (
                self.request.user.is_staff or self.request.user.is_superuser):
            return AdminUserDetailSerializer
        return UserDetailSerializer


@extend_schema_view(
    create=extend_schema(
        request=PasswordResetSerializer,
        parameters=None,
        responses=None,
        methods=["POST"],
        description="Endpoint to start password reset"
    )
)
class PasswordResetView(CreateAPIView):
    serializer_class = PasswordResetSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prt = serializer.save()

        email = serializer.validated_data.get('email')
        send_password_reset(email, prt)

        return Response({
            'detail': f'Письмо для смены пароля отправлено. Перейдите по ссылке внутри письма в течение {EMAIL_CONFIRM_TIME.seconds // 60} минут'},
            status=HTTP_201_CREATED)


@extend_schema_view(
    create=extend_schema(
        request=PasswordResetVerifySerializer,
        parameters=None,
        responses=None,
        methods=["POST"],
        description="Endpoint to verify password reset"
    )
)
class PasswordResetVerifyView(CreateAPIView):
    serializer_class = PasswordResetVerifySerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        token = get_password_reset_token(kwargs.get('token'))
        serializer = self.get_serializer(token.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('password1') == serializer.validated_data.get('password2'):
            serializer.save()
            return Response({'detail': 'Пароль успешно изменён'})
        return Response({'detail': 'Пароли должны совпадать'}, status=HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        request={
            "application/json": inline_serializer(
                name="LoginSerializer",
                fields={
                    "login": serializers.EmailField(),
                    "password": serializers.CharField(max_length=128),
                },
            ),
        },
        parameters=None,
        responses=MyTokenObtainPairSerializer,
        methods=["POST"],
        description="Endpoint to get JWT for user login"
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        if hasattr(request.data, '_mutable'):
            request.data._mutable = True
        request.data['email'] = request.data.get('login')
        if hasattr(request.data, '_mutable'):
            request.data._mutable = False
        return super().post(request, *args, **kwargs)


class TokenVerifyView(APIView):
    @extend_schema(
        request=None,
        parameters=None,
        responses=AdminUserDetailSerializer,
        methods=["POST"],
        description="Endpoint to verify user JWT and get user info"
    )
    def post(self, request: Request) -> Response:
        serializer = AdminUserDetailSerializer(request.user)
        return Response(serializer.data)


class PasswordChangeView(APIView):
    permission_classes = [IsActive, IsAuthenticated, IsEmailOwnerOrIsAdmin]

    @extend_schema(
        request=PasswordChangeSerializer,
        parameters=None,
        responses=None,
        methods=["POST"],
        description="Endpoint to change user password"
    )
    def post(self, request: Request) -> Response:
        instance = get_user(request.data.get('email'), request.data.get('old_password'))
        serializer = PasswordChangeSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('new_password1') == serializer.validated_data.get('new_password2'):
            serializer.save()

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response({'detail': 'Пароль успешно изменён!'})
        return Response({'detail': 'Пароли должны совпадать'}, status=HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    @extend_schema(
        request=RegisterSerializer,
        parameters=None,
        responses=None,
        methods=["POST"],
        description="Endpoint to register user and send email"
    )
    @transaction.atomic
    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('password1') == serializer.validated_data.get('password2'):
            user = serializer.save()
            email = serializer.validated_data.get('email')

            token = create_email_and_token(email, user)
            send_email_verify.apply_async(args=[email, token])

            return Response({
                'detail': f'Письмо для подтверждения email отправлено. Перейдите по ссылке внутри письма в течение {EMAIL_CONFIRM_TIME.seconds // 60} минут'},
                status=HTTP_201_CREATED)
        return Response({'detail': 'Пароли должны совпадать'}, status=HTTP_400_BAD_REQUEST)


class EmailVerifyView(APIView):
    @extend_schema(
        request=None,
        parameters=None,
        responses=None,
        methods=["GET"],
        description="Endpoint to verify user email"
    )
    def get(self, request: Request, token: str) -> Response:
        if verify_email(token):
            return Response({'detail': 'Электронная почта подтверждена'})
        return Response({'detail': 'Произошла ошибка подтверждения'}, status=HTTP_400_BAD_REQUEST)


class EmailChangeView(APIView):
    permission_classes = [IsActive, IsAuthenticated, IsEmailOwnerOrIsAdmin]

    @extend_schema(
        request=EmailChangeSerializer,
        parameters=None,
        responses=None,
        methods=["POST"],
        description="Endpoint to change user email"
    )
    def post(self, request: Request) -> Response:
        instance = get_user(request.data.get('email'), request.data.get('password'))
        serializer = EmailChangeSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        email = serializer.validated_data.get('new_email')
        token = create_email_and_token(email, instance)
        send_email_verify.apply_async(args=[email, token])

        return Response({
            'detail': f'Письмо для подтверждения email отправлено. Перейдите по ссылке внутри письма в течение {EMAIL_CONFIRM_TIME.seconds // 60} минут'})


class EmailResendView(APIView):
    @extend_schema(
        request=EmailResendSerializer,
        parameters=None,
        responses=None,
        methods=["POST"],
        description="Endpoint to resend email verification"
    )
    def post(self, request: Request) -> Response:
        serializer = EmailResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_address = get_email_address(serializer.validated_data.get('email'))
        tokens = get_email_address_active_tokens(email_address)
        token = tokens.first()

        if email_address.verified:
            return Response(
                {'detail': 'Данный адрес электронной почты уже активирован'}, status=HTTP_400_BAD_REQUEST)
        if not tokens:
            return Response({'detail': 'Данный адрес электронной почты не обнаружен'}, status=HTTP_400_BAD_REQUEST)
        if token.duplicated:
            return Response(
                {'detail': f'Превышено количество попыток'}, status=HTTP_400_BAD_REQUEST)

        token.duplicated = True
        token.save()
        send_email_verify.apply_async(args=[email_address.email_address, token.token])
        return Response({
            'detail': f'Письмо для подтверждения email отправлено. Перейдите по ссылке внутри письма в течение {EMAIL_CONFIRM_TIME.seconds // 60} минут'})


class PasswordResendView(APIView):
    @extend_schema(
        request=PasswordResendSerializer,
        parameters=None,
        responses=None,
        methods=["POST"],
        description="Endpoint to resend password reset email"
    )
    def post(self, request: Request) -> Response:
        serializer = PasswordResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        user = get_user_by_email(email)
        tokens = get_password_active_tokens(user)
        token = tokens.first()

        if not tokens:
            return Response({'detail': 'Данный пользователь не обнаружен'}, status=HTTP_400_BAD_REQUEST)
        if token.duplicated:
            return Response(
                {'detail': f'Превышено количество попыток'}, status=HTTP_400_BAD_REQUEST)

        token.duplicated = True
        token.save()
        send_password_reset.apply_async(args=[email, token])
        return Response({
            'detail': f'Письмо для подтверждения email отправлено. Перейдите по ссылке внутри письма в течение {EMAIL_CONFIRM_TIME.seconds // 60} минут'})
