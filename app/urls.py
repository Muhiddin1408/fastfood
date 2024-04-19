from django.urls import path

from app.views import *

urlpatterns = [
    path('register', register),
    path('login', login),

    path('get-menu', MenuView.as_view()),
    path('post-menu', MenuCreateView.as_view()),
    path('post/order/item', OrderItemCreate.as_view()),
    path('post/order', ToOrder.as_view()),
    path('get/order/<str:q>', get_order),
    path('get/order/status', order_status),
]
