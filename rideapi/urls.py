from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RideViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('rides', RideViewSet)

urlpatterns = router.urls
