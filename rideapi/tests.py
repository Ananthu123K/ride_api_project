from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Ride



# Create your tests here.

# JWT Helper
def get_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class RideAPITestCase(APITestCase):

    def setUp(self):
        # Users
        self.rider = User.objects.create_user(
            username='rider', password='1234'
        )
        self.driver = User.objects.create_user(
            username='driver', password='1234'
        )

        # Initial Ride
        self.ride = Ride.objects.create(
            rider=self.rider,
            pickup_location='Kochi',
            dropoff_location='Trivandrum'
        )

     # AUTH HELPER

    def authenticate(self, user):
        token = get_token(user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token
        )


    # JUNIOR LEVEL TESTS


    def test_ride_model_creation(self):
        """Ride model default status"""
        self.assertEqual(self.ride.status, 'requested')

    def test_create_ride_api(self):
        """Authenticated user can create ride"""
        self.authenticate(self.rider)

        response = self.client.post('/api/rides/', {
            'pickup_location': 'Aluva',
            'dropoff_location': 'Kakkanad'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_rides(self):
        """List all rides"""
        self.authenticate(self.rider)

        response = self.client.get('/api/rides/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authentication_required(self):
        """Unauthenticated access blocked"""
        response = self.client.get('/api/rides/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    #  SENIOR LEVEL TESTS


    def test_driver_accept_ride(self):
        """Driver accepts a ride"""
        self.authenticate(self.driver)

        response = self.client.post(
            f'/api/rides/{self.ride.id}/accept_ride/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'accepted')

    def test_ride_matching_algorithm(self):
        """Driver auto-matched to pending ride"""
        self.authenticate(self.driver)

        response = self.client.post('/api/rides/match_ride/')
        self.assertEqual(response.status_code, 200)

    def test_valid_status_flow(self):
        """requested → accepted → started → completed"""
        self.authenticate(self.driver)
        self.client.post(
            f'/api/rides/{self.ride.id}/accept_ride/'
        )

        self.authenticate(self.rider)
        response = self.client.post(
            f'/api/rides/{self.ride.id}/update_status/',
            {'status': 'started'}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            f'/api/rides/{self.ride.id}/update_status/',
            {'status': 'completed'}
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_status_transition(self):
        """Invalid status change blocked"""
        self.authenticate(self.rider)

        response = self.client.post(
            f'/api/rides/{self.ride.id}/update_status/',
            {'status': 'completed'}
        )

        self.assertEqual(response.status_code, 400)

    def test_real_time_tracking_simulation(self):
        """Simulated GPS update"""
        self.authenticate(self.driver)

        response = self.client.post(
            f'/api/rides/{self.ride.id}/update_location/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('current_lat', response.data)
        self.assertIn('current_lng', response.data)
