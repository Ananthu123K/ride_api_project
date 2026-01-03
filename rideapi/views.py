from django.shortcuts import render
import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User

from .models import Ride
from .serializers import UserSerializer, RideSerializer

# Create your views here.



# USER REGISTRATION
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# RIDE APIs
class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all().order_by('-created_at')
    serializer_class = RideSerializer

    def perform_create(self, serializer):
        serializer.save(rider=self.request.user)

    # UPDATE RIDE STATUS
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        ride = self.get_object()
        new_status = request.data.get('status')

        valid_flow = {
            'requested': ['accepted', 'cancelled'],
            'accepted': ['started', 'cancelled'],
            'started': ['completed'],
        }

        if ride.status in valid_flow and new_status in valid_flow[ride.status]:
            ride.status = new_status
            ride.save()
            return Response(RideSerializer(ride).data)

        return Response(
            {'error': 'Invalid status transition'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # REAL-TIME LOCATION SIMULATION
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        ride = self.get_object()
        ride.current_lat = round(random.uniform(8.0, 13.0), 6)
        ride.current_lng = round(random.uniform(76.0, 80.0), 6)
        ride.save()
        return Response(RideSerializer(ride).data)

    # DRIVER ACCEPT RIDE
    @action(detail=True, methods=['post'])
    def accept_ride(self, request, pk=None):
        ride = self.get_object()
        if ride.driver:
            return Response({'error': 'Ride already assigned'}, status=400)

        ride.driver = request.user
        ride.status = 'accepted'
        ride.save()
        return Response(RideSerializer(ride).data)

    # RIDE MATCHING 
    @action(detail=False, methods=['post'])
    def match_ride(self, request):
        ride = Ride.objects.filter(status='requested', driver__isnull=True).first()
        if not ride:
            return Response({'message': 'No pending rides'}, status=404)

        ride.driver = request.user
        ride.status = 'accepted'
        ride.save()
        return Response(RideSerializer(ride).data)
