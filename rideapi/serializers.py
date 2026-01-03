from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ride

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RideSerializer(serializers.ModelSerializer):
    rider = serializers.StringRelatedField(read_only=True)
    driver = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Ride
        fields = '__all__'
