from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, TouristPlace, Review, LocalService,
    Booking, Notification, FavouritePlace
)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'preferences']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.get_or_create(user=user)
        return user


class TouristPlaceSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = TouristPlace
        fields = ['place_id', 'name', 'category', 'description', 'location_lat',
                  'location_lng', 'rating', 'average_rating', 'review_count',
                  'images', 'visiting_hours', 'created_at', 'updated_at']
        read_only_fields = ['place_id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    place_name = serializers.CharField(source='place.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'place', 'place_name', 'rating',
                  'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LocalServiceSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = LocalService
        fields = ['service_id', 'name', 'type', 'address', 'contact',
                  'location_lat', 'location_lng', 'rating', 'average_rating',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['service_id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        return obj.rating


class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'username', 'service', 'service_name', 'status',
                  'booking_date', 'scheduled_date', 'number_of_guests', 'notes',
                  'updated_at']
        read_only_fields = ['id', 'user', 'booking_date', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'username', 'message', 'date', 'is_read']
        read_only_fields = ['id', 'user', 'date']


class FavouritePlaceSerializer(serializers.ModelSerializer):
    place_details = TouristPlaceSerializer(source='place', read_only=True)

    class Meta:
        model = FavouritePlace
        fields = ['id', 'user', 'place', 'place_details', 'added_at']
        read_only_fields = ['id', 'user', 'added_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
