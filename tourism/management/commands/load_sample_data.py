from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from tourism.models import (
    Booking,
    FavouritePlace,
    LocalService,
    Notification,
    Review,
    TouristPlace,
    UserProfile,
)


class Command(BaseCommand):
    help = 'Load demo tourism data into the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading demo data...'))

        places_data = [
            {
                'name': 'Shri Krishna Janmabhoomi',
                'category': 'temple',
                'description': 'The sacred birthplace of Lord Krishna and one of the most important darshan sites in Mathura.',
                'location_lat': 27.4898,
                'location_lng': 77.6758,
                'visiting_hours': '5:00 AM - 12:00 PM, 4:00 PM - 10:00 PM',
                'rating': 4.8,
            },
            {
                'name': 'Dwarkadhish Temple',
                'category': 'temple',
                'description': 'A beautiful Krishna temple known for its lively aarti, ornate architecture, and deep devotional atmosphere.',
                'location_lat': 27.4902,
                'location_lng': 77.6845,
                'visiting_hours': '6:00 AM - 1:00 PM, 3:00 PM - 9:00 PM',
                'rating': 4.7,
            },
            {
                'name': 'Vishram Ghat',
                'category': 'ghat',
                'description': 'The most sacred Yamuna ghat in Mathura, believed to be where Krishna rested after defeating Kansa.',
                'location_lat': 27.4920,
                'location_lng': 77.6980,
                'visiting_hours': '4:00 AM - 10:00 PM',
                'rating': 4.6,
            },
            {
                'name': 'Mathura Museum',
                'category': 'museum',
                'description': 'A heritage museum with ancient sculptures, coins, inscriptions, and artifacts from Mathura history.',
                'location_lat': 27.4850,
                'location_lng': 77.7010,
                'visiting_hours': '10:00 AM - 5:00 PM (Closed Mondays)',
                'rating': 4.5,
            },
            {
                'name': 'Kusum Sarovar',
                'category': 'park',
                'description': 'A peaceful water tank and garden area connected with Radha-Krishna leelas and quiet evening walks.',
                'location_lat': 27.4750,
                'location_lng': 77.6850,
                'visiting_hours': '6:00 AM - 8:00 PM',
                'rating': 4.4,
            },
            {
                'name': 'Gita Mandir',
                'category': 'temple',
                'description': 'A serene temple famous for inscriptions of the Bhagavad Gita and peaceful darshan spaces.',
                'location_lat': 27.4719,
                'location_lng': 77.6768,
                'visiting_hours': '6:00 AM - 8:30 PM',
                'rating': 4.5,
            },
            {
                'name': 'Prem Mandir Vrindavan',
                'category': 'temple',
                'description': 'A grand marble temple in nearby Vrindavan, known for evening lights and devotional scenes.',
                'location_lat': 27.5706,
                'location_lng': 77.6593,
                'visiting_hours': '5:30 AM - 12:00 PM, 4:30 PM - 8:30 PM',
                'rating': 4.9,
            },
            {
                'name': 'Banke Bihari Temple',
                'category': 'temple',
                'description': 'One of Vrindavan’s most loved temples, known for intense bhakti and crowded festival darshan.',
                'location_lat': 27.5806,
                'location_lng': 77.7006,
                'visiting_hours': '7:45 AM - 12:00 PM, 5:30 PM - 9:30 PM',
                'rating': 4.9,
            },
            {
                'name': 'Radha Kund',
                'category': 'ghat',
                'description': 'A highly sacred kund associated with Radha Rani, visited by devotees for parikrama and prayer.',
                'location_lat': 27.5240,
                'location_lng': 77.4912,
                'visiting_hours': 'Open 24 hours',
                'rating': 4.7,
            },
            {
                'name': 'Govardhan Hill',
                'category': 'other',
                'description': 'A sacred parikrama route connected with Krishna lifting Govardhan to protect Braj devotees.',
                'location_lat': 27.4965,
                'location_lng': 77.4628,
                'visiting_hours': 'Open 24 hours',
                'rating': 4.8,
            },
            {
                'name': 'Raman Reti',
                'category': 'park',
                'description': 'A soft sandy devotional area where devotees meditate, sit quietly, and remember Krishna’s childhood leelas.',
                'location_lat': 27.5724,
                'location_lng': 77.6729,
                'visiting_hours': '5:00 AM - 8:00 PM',
                'rating': 4.4,
            },
            {
                'name': 'Kans Qila',
                'category': 'other',
                'description': 'An old fort site linked with King Kansa and the historic landscape of Mathura city.',
                'location_lat': 27.4990,
                'location_lng': 77.6808,
                'visiting_hours': '9:00 AM - 6:00 PM',
                'rating': 4.0,
            },
            {
                'name': 'Potra Kund',
                'category': 'ghat',
                'description': 'A sacred kund close to Krishna Janmabhoomi, associated with childhood stories of Lord Krishna.',
                'location_lat': 27.4908,
                'location_lng': 77.6746,
                'visiting_hours': '6:00 AM - 8:00 PM',
                'rating': 4.3,
            },
            {
                'name': 'Seva Kunj Vrindavan',
                'category': 'park',
                'description': 'A devotional garden believed to be connected with Radha-Krishna rasa leela traditions.',
                'location_lat': 27.5820,
                'location_lng': 77.6950,
                'visiting_hours': '8:00 AM - 7:00 PM',
                'rating': 4.6,
            },
            {
                'name': 'Nidhivan',
                'category': 'park',
                'description': 'A mystical Vrindavan grove known for deep devotional belief and evening closure traditions.',
                'location_lat': 27.5819,
                'location_lng': 77.6956,
                'visiting_hours': '6:00 AM - 7:00 PM',
                'rating': 4.7,
            },
        ]

        for place_data in places_data:
            place, created = TouristPlace.objects.update_or_create(
                name=place_data['name'],
                defaults=place_data,
            )
            self.write_result(created, 'place', place.name)

        services_data = [
            ('Braj Bhakti Guest House', 'hotel', 'Near Krishna Janmabhoomi', '9876543210', 27.4900, 77.6764, 4.4, 'Budget stay close to Janmabhoomi with simple rooms for pilgrims.'),
            ('Yamuna View Residency', 'hotel', 'Vishram Ghat Road', '9876543211', 27.4922, 77.6977, 4.5, 'Comfortable rooms near Yamuna aarti and old city lanes.'),
            ('Govardhan Palace Hotel', 'hotel', 'Mathura-Vrindavan Road', '9876543212', 27.5110, 77.6710, 4.2, 'Mid-range family hotel with easy access to Mathura and Vrindavan.'),
            ('Radhe Radhe Dharamshala', 'hotel', 'Dwarkadhish Temple Area', '9876543213', 27.4908, 77.6848, 4.1, 'Simple pilgrim accommodation near temple markets.'),
            ('Shri Krishna Suites', 'hotel', 'Janmabhoomi Link Road', '9876543214', 27.4886, 77.6782, 4.6, 'Premium stay with clean rooms, parking, and family facilities.'),
            ('Bhakti Bhojanalaya', 'restaurant', 'Main Bazaar', '9876543215', 27.4880, 77.6920, 4.6, 'Pure vegetarian thali, kachori, sabzi, and fresh sweets.'),
            ('Brijwasi Sweets Corner', 'restaurant', 'Holigate Market', '9876543216', 27.4943, 77.6874, 4.7, 'Popular peda, lassi, snacks, and festival sweets.'),
            ('Govinda Sattvik Rasoi', 'restaurant', 'Near Dwarkadhish Temple', '9876543217', 27.4911, 77.6846, 4.5, 'Sattvik meals for devotees and family groups.'),
            ('Yamuna Cafe', 'cafe', 'Vishram Ghat Lane', '9876543218', 27.4927, 77.6971, 4.3, 'Tea, coffee, snacks, and light meals near the ghats.'),
            ('Braj Brew Cafe', 'cafe', 'Mathura Museum Road', '9876543219', 27.4863, 77.7006, 4.2, 'Modern cafe with Wi-Fi, quick bites, and coffee.'),
            ('Mathura E-Rickshaw Seva', 'transport', 'Railway Station', '9876543220', 27.4829, 77.6720, 4.4, 'Local e-rickshaw support for temple hopping and market rides.'),
            ('Braj Darshan Taxi', 'transport', 'Bus Stand Road', '9876543221', 27.4890, 77.7110, 4.5, 'Taxi service for Mathura, Vrindavan, Govardhan, and Barsana routes.'),
            ('Vrindavan Shuttle Service', 'transport', 'Mathura-Vrindavan Road', '9876543222', 27.5300, 77.6650, 4.1, 'Shared shuttle service between Mathura and Vrindavan.'),
            ('Pilgrim Guide Desk', 'transport', 'Tourist Information Center', '9876543223', 27.4910, 77.6850, 4.3, 'Local guide and route planning help for first-time visitors.'),
            ('Aarti Boat Assistance', 'transport', 'Vishram Ghat', '9876543224', 27.4921, 77.6982, 4.0, 'Boat and ghat assistance during morning and evening aarti hours.'),
        ]

        for name, service_type, address, contact, lat, lng, rating, description in services_data:
            service, created = LocalService.objects.update_or_create(
                name=name,
                defaults={
                    'type': service_type,
                    'address': address,
                    'contact': contact,
                    'location_lat': lat,
                    'location_lng': lng,
                    'rating': rating,
                    'description': description,
                },
            )
            self.write_result(created, 'service', service.name)

        admin_user = self.ensure_user(
            username='admin',
            password='admin12345',
            email='admin@mathuradarshan.local',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True,
        )

        demo_users = [
            self.ensure_user('tourist', 'tourist123', 'tourist@example.com', 'Test', 'Tourist'),
            self.ensure_user('radha', 'radha123', 'radha@example.com', 'Radha', 'Sharma'),
            self.ensure_user('mohan', 'mohan123', 'mohan@example.com', 'Mohan', 'Verma'),
            self.ensure_user('priya', 'priya123', 'priya@example.com', 'Priya', 'Gupta'),
        ]

        for user in [admin_user, *demo_users]:
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'phone': '9999999999',
                    'preferences': 'Temple darshan, sattvik food, peaceful ghats',
                },
            )

        places = list(TouristPlace.objects.order_by('place_id'))
        services = list(LocalService.objects.order_by('service_id'))

        review_comments = [
            'Very peaceful darshan and well managed place.',
            'Beautiful spiritual atmosphere, best visited early morning.',
            'Helpful locals and a strong feeling of bhakti.',
            'Good for families, but weekends can be crowded.',
            'A must visit during Mathura yatra.',
        ]
        review_count = 0
        for index, place in enumerate(places[:15]):
            user = demo_users[index % len(demo_users)]
            review, created = Review.objects.update_or_create(
                user=user,
                place=place,
                defaults={
                    'rating': max(4, min(5, round(place.rating))),
                    'comment': review_comments[index % len(review_comments)],
                },
            )
            if created:
                review_count += 1

        for index, place in enumerate(places[:10]):
            FavouritePlace.objects.get_or_create(
                user=demo_users[index % len(demo_users)],
                place=place,
            )

        statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        for index, service in enumerate(services[:12]):
            Booking.objects.update_or_create(
                user=demo_users[index % len(demo_users)],
                service=service,
                defaults={
                    'status': statuses[index % len(statuses)],
                    'scheduled_date': timezone.now() + timedelta(days=index + 1),
                    'number_of_guests': (index % 5) + 1,
                    'notes': 'Demo booking for Mathura yatra planning.',
                },
            )

        notifications = [
            'Your darshan plan is ready for review.',
            'Evening Yamuna aarti starts around sunset today.',
            'Remember to carry ID proof for hotel check-in.',
            'Govardhan parikrama is best started early morning.',
        ]
        for index, user in enumerate(demo_users):
            Notification.objects.get_or_create(
                user=user,
                message=notifications[index % len(notifications)],
                defaults={'is_read': index % 2 == 0},
            )

        self.stdout.write(self.style.SUCCESS('\nDemo data loaded successfully.'))
        self.stdout.write('Created/updated: 15 places, 15 services, 5 users, reviews, favourites, bookings, notifications.')
        self.stdout.write('Admin login: username=admin, password=admin12345')
        self.stdout.write('Demo user: username=tourist, password=tourist123')

    def ensure_user(
        self,
        username,
        password,
        email,
        first_name='',
        last_name='',
        is_staff=False,
        is_superuser=False,
    ):
        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()
        self.write_result(created, 'user', username)
        return user

    def write_result(self, created, label, name):
        status = 'Created' if created else 'Updated'
        self.stdout.write(f'{status} {label}: {name}')
