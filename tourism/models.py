from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """Extended user profile with additional information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    preferences = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class TouristPlace(models.Model):
    """Tourist places in Mathura with location and details."""
    CATEGORY_CHOICES = [
        ('temple', 'Temple'),
        ('ghat', 'Ghat'),
        ('museum', 'Museum'),
        ('park', 'Park'),
        ('other', 'Other'),
    ]

    place_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    location_lat = models.FloatField()
    location_lng = models.FloatField()
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    images = models.ImageField(upload_to='places/', blank=True, null=True)
    visiting_hours = models.CharField(max_length=100, default='9:00 AM - 6:00 PM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tourist Place'
        verbose_name_plural = 'Tourist Places'
        ordering = ['-rating', 'name']


class Review(models.Model):
    """Reviews for tourist places."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    place = models.ForeignKey(TouristPlace, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review of {self.place.name} by {self.user.username}"

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('user', 'place')
        ordering = ['-created_at']


class LocalService(models.Model):
    """Local services like hotels, restaurants, transport, cafes."""
    SERVICE_TYPE_CHOICES = [
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
        ('transport', 'Transport'),
        ('cafe', 'Cafe'),
    ]

    service_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    address = models.TextField()
    contact = models.CharField(max_length=20)
    location_lat = models.FloatField()
    location_lng = models.FloatField()
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type})"

    class Meta:
        verbose_name = 'Local Service'
        verbose_name_plural = 'Local Services'
        ordering = ['-rating', 'name']


class Booking(models.Model):
    """Bookings for local services."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(LocalService, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    number_of_guests = models.IntegerField(default=1)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking of {self.service.name} by {self.user.username}"

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-booking_date']


class Notification(models.Model):
    """Notifications for users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date']


class FavouritePlace(models.Model):
    """Favourite places saved by users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    place = models.ForeignKey(TouristPlace, on_delete=models.CASCADE, related_name='favourited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.place.name}"

    class Meta:
        verbose_name = 'Favourite Place'
        verbose_name_plural = 'Favourite Places'
        unique_together = ('user', 'place')
        ordering = ['-added_at']


class ChatHistory(models.Model):
    """Saved chatbot conversations for logged-in users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_histories')
    user_message = models.TextField()
    assistant_response = models.TextField()
    weather_info = models.TextField(blank=True, default='')
    model_name = models.CharField(max_length=120, blank=True, default='')
    finish_reason = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat by {self.user.username} on {self.created_at:%d %b %Y %H:%M}"

    class Meta:
        verbose_name = 'Chat History'
        verbose_name_plural = 'Chat Histories'
        ordering = ['-created_at']


class TripPlan(models.Model):
    """Saved AI-generated trip plans for logged-in users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_plans')
    trip_title = models.CharField(max_length=255, blank=True, default='')
    duration_days = models.PositiveIntegerField(default=1)
    travelers = models.PositiveIntegerField(default=1)
    budget_style = models.CharField(max_length=30, blank=True, default='')
    input_payload = models.JSONField(default=dict, blank=True)
    plan_payload = models.JSONField(default=dict, blank=True)
    raw_response = models.TextField(blank=True, default='')
    model_name = models.CharField(max_length=120, blank=True, default='')
    finish_reason = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        title = self.trip_title or f"{self.duration_days}-day trip"
        return f"{title} - {self.user.username}"

    class Meta:
        verbose_name = 'Trip Plan'
        verbose_name_plural = 'Trip Plans'
        ordering = ['-created_at']


class TempleGuide(models.Model):
    """Structured temple timing and details knowledge base."""
    name = models.CharField(max_length=255, unique=True)
    region = models.CharField(max_length=100, blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='temple')
    location_text = models.TextField(blank=True, default='')
    famous_for = models.TextField(blank=True, default='')
    history = models.TextField(blank=True, default='')
    main_deity = models.CharField(max_length=255, blank=True, default='')
    best_time_to_visit = models.CharField(max_length=255, blank=True, default='')
    best_season = models.CharField(max_length=120, blank=True, default='')
    crowd_level = models.CharField(max_length=80, blank=True, default='')
    average_visit_duration = models.CharField(max_length=80, blank=True, default='')
    photography_policy = models.CharField(max_length=255, blank=True, default='')
    dress_code = models.CharField(max_length=255, blank=True, default='')
    entry_fee = models.CharField(max_length=120, blank=True, default='')
    vip_darshan = models.CharField(max_length=120, blank=True, default='')
    nearby_attractions = models.JSONField(default=list, blank=True)
    parking_info = models.CharField(max_length=255, blank=True, default='')
    google_map_keyword = models.CharField(max_length=255, blank=True, default='')
    local_market_food = models.TextField(blank=True, default='')
    timings = models.JSONField(default=list, blank=True)
    important_tips = models.JSONField(default=list, blank=True)
    aliases = models.JSONField(default=list, blank=True)
    source_note = models.CharField(max_length=255, blank=True, default='Mathura-Vrindavan Darshan Guide 2026')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Temple Guide'
        verbose_name_plural = 'Temple Guides'
        ordering = ['region', 'name']
