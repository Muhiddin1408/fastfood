from rest_framework import serializers, status
from rest_framework.response import Response

from app.models import Menu, ImageMenu, OrderItem, Order


class ProductsImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ImageMenu
        fields = '__all__'


class SerializerMenu(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Menu
        fields = ('id', 'name', 'type', 'price', 'description', 'image', 'uploaded_images')

    def get_image(self, obj):
        image = ImageMenu.objects.filter(menu=obj)
        return ProductsImageSerializers(image, many=True).data

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")
        request = self.context['request']
        if request.user == 'waiter' or request.user == 'admin':
            product = Menu.objects.create(**validated_data)
            for image in uploaded_images:
                ImageMenu.objects.create(product=product, image=image)

            return product


# ORDER


class OrderItemSerializers(serializers.ModelSerializer):
    product = SerializerMenu(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'count', 'product')


class OrderViewSerializer(serializers.ModelSerializer):
    order_item = OrderItemSerializers(many=True, read_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'payment_status', 'delivered_time', 'lat', 'lon', 'order_item')

    def get_user(self, obj):
        return obj.user.username


