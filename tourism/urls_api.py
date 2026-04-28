from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import (
    UserRegistrationViewSet, UserViewSet, TouristPlaceViewSet,
    ReviewViewSet, LocalServiceViewSet, BookingViewSet,
    NotificationViewSet, FavouritePlaceViewSet
)

router = DefaultRouter()
router.register(r'register', UserRegistrationViewSet, basename='register')
router.register(r'users', UserViewSet, basename='users')
router.register(r'places', TouristPlaceViewSet, basename='places')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'services', LocalServiceViewSet, basename='services')
router.register(r'bookings', BookingViewSet, basename='bookings')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'favourites', FavouritePlaceViewSet, basename='favourites')

urlpatterns = [
    path('', include(router.urls)),
]
