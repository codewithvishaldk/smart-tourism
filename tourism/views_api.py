from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q
import math

from .models import (
    TouristPlace, Review, LocalService, Booking,
    Notification, FavouritePlace
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, TouristPlaceSerializer,
    ReviewSerializer, LocalServiceSerializer, BookingSerializer,
    NotificationSerializer, FavouritePlaceSerializer
)


class UserRegistrationViewSet(viewsets.ViewSet):
    """User registration endpoint."""
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User registered successfully',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ViewSet):
    """User profile endpoints."""
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        if user:
            return Response({'user': UserSerializer(user).data})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class TouristPlaceViewSet(viewsets.ModelViewSet):
    """Tourist places viewset with filtering and nearby search."""
    queryset = TouristPlace.objects.all()
    serializer_class = TouristPlaceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'place_id'

    def get_queryset(self):
        queryset = TouristPlace.objects.all()
        category = self.request.query_params.get('category')
        query = self.request.query_params.get('query')
        if category:
            queryset = queryset.filter(category=category)
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(visiting_hours__icontains=query)
            )
        return queryset

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        query = (request.query_params.get('query') or '').strip()
        if len(query) < 2:
            return Response([])

        places = TouristPlace.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).order_by('-rating', 'name')[:8]

        data = [
            {
                'place_id': place.place_id,
                'name': place.name,
                'category': place.get_category_display(),
                'location_lat': place.location_lat,
                'location_lng': place.location_lng,
                'rating': place.rating,
            }
            for place in places
        ]
        return Response(data)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get nearby tourist places."""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 5))  # Default 5 km

        if not lat or not lng:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat, lng = float(lat), float(lng)
        except ValueError:
            return Response(
                {'error': 'Invalid latitude or longitude'},
                status=status.HTTP_400_BAD_REQUEST
            )

        places = TouristPlace.objects.all()
        nearby_places = []

        for place in places:
            distance = self.calculate_distance(lat, lng, place.location_lat, place.location_lng)
            if distance <= radius:
                nearby_places.append((place, distance))

        nearby_places.sort(key=lambda x: x[1])
        places = [p[0] for p in nearby_places]

        serializer = self.get_serializer(places, many=True)
        return Response(serializer.data)

    @staticmethod
    def calculate_distance(lat1, lng1, lat2, lng2):
        """Calculate distance between two coordinates in kilometers."""
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c


class ReviewViewSet(viewsets.ModelViewSet):
    """Review viewset."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        place_id = self.request.query_params.get('place_id')
        if place_id:
            return Review.objects.filter(place__place_id=place_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Please log in before submitting a review.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_place(self, request):
        """Get reviews by place ID."""
        place_id = request.query_params.get('place_id')
        if not place_id:
            return Response(
                {'error': 'place_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reviews = Review.objects.filter(place__place_id=place_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class LocalServiceViewSet(viewsets.ModelViewSet):
    """Local services viewset."""
    queryset = LocalService.objects.all()
    serializer_class = LocalServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'service_id'

    def get_queryset(self):
        queryset = LocalService.objects.all()
        service_type = self.request.query_params.get('type')
        if service_type:
            queryset = queryset.filter(type=service_type)
        return queryset

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get nearby services."""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 5))
        service_type = request.query_params.get('type')

        if not lat or not lng:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat, lng = float(lat), float(lng)
        except ValueError:
            return Response(
                {'error': 'Invalid latitude or longitude'},
                status=status.HTTP_400_BAD_REQUEST
            )

        services = LocalService.objects.all()
        if service_type:
            services = services.filter(type=service_type)

        nearby_services = []
        for service in services:
            distance = self.calculate_distance(lat, lng, service.location_lat, service.location_lng)
            if distance <= radius:
                nearby_services.append((service, distance))

        nearby_services.sort(key=lambda x: x[1])
        services = [s[0] for s in nearby_services]

        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data)

    @staticmethod
    def calculate_distance(lat1, lng1, lat2, lng2):
        """Calculate distance between two coordinates in kilometers."""
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c


class BookingViewSet(viewsets.ModelViewSet):
    """Booking viewset."""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """Notification viewset."""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})


class FavouritePlaceViewSet(viewsets.ModelViewSet):
    """Favourite places viewset."""
    queryset = FavouritePlace.objects.all()
    serializer_class = FavouritePlaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavouritePlace.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_favourite(self, request):
        place_id = request.data.get('place_id')
        if not place_id:
            return Response(
                {'error': 'place_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            place = TouristPlace.objects.get(place_id=place_id)
        except TouristPlace.DoesNotExist:
            return Response(
                {'error': 'Place not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        favourite, created = FavouritePlace.objects.get_or_create(
            user=request.user,
            place=place
        )

        if created:
            return Response(
                {'status': 'Place added to favourites'},
                status=status.HTTP_201_CREATED
            )
        return Response({'status': 'Place already in favourites'})

    @action(detail=False, methods=['post'])
    def remove_favourite(self, request):
        place_id = request.data.get('place_id')
        if not place_id:
            return Response(
                {'error': 'place_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            favourite = FavouritePlace.objects.get(
                user=request.user,
                place__place_id=place_id
            )
            favourite.delete()
            return Response({'status': 'Place removed from favourites'})
        except FavouritePlace.DoesNotExist:
            return Response(
                {'error': 'Favourite not found'},
                status=status.HTTP_404_NOT_FOUND
            )
