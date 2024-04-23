from math import radians, sin, cos, sqrt, atan2

from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import permission_classes, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import User, Menu, Order, OrderItem
from app.serializers import SerializerMenu, OrderItemSerializers, OrderViewSerializer


class SmallPagesPagination(PageNumberPagination):
    page_size = 20

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny, ])
def register(request):
    try:
        username = request.data.get('username')
        if not username:
            res = {
                'msg': 'Login empty',
                'status': 0,
            }
            return Response(res)
        user = User.objects.filter(username=username)
        if not user:
            number = User.objects.create(
                    username=username,
                    status='user'
                )
            number.set_password(request.data.get('password'))
            number.save()

            result = {
                'status': 1
            }
            return Response(result, status=status.HTTP_200_OK)
        else:
            res = {
                'status': 0,
                'msg': 'this user has already registered'
            }

            return Response(res, status=status.HTTP_200_OK)
    except KeyError:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def login(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user.check_password(password):
            user.save()
            token = RefreshToken.for_user(user)
            result = {
                'access': str(token.access_token),
                'refresh': str(token),
            }
            return Response(result, status=status.HTTP_200_OK)
        else:
            res = {
                'status': 0,
                'msg': 'Username or password is incorrect'
            }
            return Response(res,  status=status.HTTP_200_OK)
    except KeyError:
        res = {
            'status': 0,
            'msg': 'Please set all reqiured fields'
        }
        return Response(res)


# MENU

class MenuView(generics.ListAPIView):
    queryset = Menu.objects.all()
    serializer_class = SerializerMenu
    permission_classes = [AllowAny]
    pagination_class = SmallPagesPagination


# Order


class OrderItemCreate(generics.CreateAPIView):
    queryset = OrderItem.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            if request.user.status == 'user' or request.user.status == 'admin':
                data = self.request.data
                order = Order.objects.filter(user=request.user, status='basket').last()
                if not order:
                    order = Order.objects.create(
                        user=request.user,
                        status='basket',
                    )

                OrderItem.objects.create(
                    order=order,
                    product_id=data['product_id'],
                    count=data['count'],
                )
            return Response(status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ToOrder(generics.CreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = self.request.data
        order = Order.objects.filter(user=request.user, status='basket').first()
        queue_count = OrderItem.objects.filter(order__status='wait', product__type='food').count()
        queue_count_self = OrderItem.objects.filter(order=order, product__type='food').count()

        if (queue_count+queue_count_self) % 4 == 0 or queue_count+queue_count_self <= 4:
            time = ((queue_count+queue_count_self) % 4) * 5
        else:
            time = (((queue_count+queue_count_self) % 4) + 1) * 5
        lat1 = radians(69.287803)
        lon1 = radians(41.358240)
        lat2 = radians(data['lat'])
        lon2 = radians(data['lon'])
        d_lat = lat2 - lat1
        d_lon = lon2 - lon1
        a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        r = 6371.0
        distance = r * c
        if distance % 1 == 0:
            d_time = distance * 3
        else:
            d_time = (distance + 1) * 3
        time = time + d_time
        order.lat = data['lat']
        order.lon = data['lon']
        order.payment_status = data['payment']
        order.delivered_time = time
        order.status = 'wait'
        order.save()

        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_order(request, q):
    if request.user == 'waiter' or request.user == 'admin':
        order = Order.objects.filter(status=q)
        return Response(OrderViewSerializer(order, many=True).data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, ])
def order_status(request, pk):
    if request.user == 'waiter' or request.user == 'admin':
        order = Order.objects.get(id=pk)
        if order.status == 'wait':
            order.status = 'sent'
            order.save()
        elif order.status == 'sent':
            order.status = 'delivered'
            order.save()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


# Admin


class MenuCreateView(generics.CreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = SerializerMenu
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializers = SerializerMenu(request.data)
        if request.user.status == 'waiter' or request.user.status == 'admin' and serializers.is_valid():
            serializers.save()
            return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, ])
def delete_menu(request, pk):
    if request.user.status == 'waiter' or request.user.status == 'admin':
        menu = Menu.objects.get(id=pk)
        menu.delete()
    return Response(status=status.HTTP_200_OK)


