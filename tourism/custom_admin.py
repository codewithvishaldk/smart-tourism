from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q, Avg
import csv
from datetime import timedelta
from django.utils import timezone
import json
from .models import (
    UserProfile, TouristPlace, Review, LocalService,
    Booking, Notification, FavouritePlace, ChatHistory, TripPlan, TempleGuide
)


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with dashboard"""
    site_header = "Mathura Darshan Admin"
    site_title = "Mathura Tourism Admin"
    index_title = "Welcome to Admin Dashboard"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.admin_site_dashboard), name='admin_dashboard'),
            path('reports/', self.admin_view(self.admin_reports), name='admin_reports'),
            path('reports/print/', self.admin_view(self.admin_reports_print), name='admin_reports_print'),
        ]
        return custom_urls + urls

    @staticmethod
    def _safe_image_url(field):
        try:
            return field.url if field else ""
        except Exception:
            return ""

    @staticmethod
    def _parse_float(value, default=0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _report_window_map():
        return {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "all": None,
        }

    def _report_filter_options(self):
        place_categories = [
            {"value": value, "label": label}
            for value, label in TouristPlace.CATEGORY_CHOICES
        ]
        service_types = [
            {"value": value, "label": label}
            for value, label in LocalService.SERVICE_TYPE_CHOICES
        ]
        booking_statuses = [
            {"value": value, "label": label}
            for value, label in Booking.STATUS_CHOICES
        ]
        return {
            "place_category_options": place_categories,
            "service_type_options": service_types,
            "booking_status_options": booking_statuses,
        }

    @staticmethod
    def _get_rush_level(review_count, favorite_count, rating):
        score = (review_count * 1.8) + (favorite_count * 1.2) + (rating * 2)
        if score >= 20:
            return "high", score
        if score >= 11:
            return "medium", score
        return "low", score

    def _get_report_filters(self, request):
        return {
            "window": self._get_report_window_value(request),
            "scope": self._get_report_scope_value(request),
            "query": request.GET.get("query", "").strip(),
            "place_category": request.GET.get("place_category", "").strip(),
            "service_type": request.GET.get("service_type", "").strip(),
            "booking_status": request.GET.get("booking_status", "").strip(),
            "min_rating": request.GET.get("min_rating", "").strip(),
            "has_image": request.GET.get("has_image", "").strip(),
        }

    def _apply_report_filters(self, filters):
        window_map = self._report_window_map()
        report_window = window_map.get(filters["window"], timedelta(days=30))
        report_start = timezone.now() - report_window if report_window else None

        bookings = Booking.objects.select_related("service", "user").order_by("-booking_date")
        places = TouristPlace.objects.order_by("-created_at", "-rating")
        services = LocalService.objects.order_by("-created_at", "-rating")
        reviews = Review.objects.select_related("place", "user").order_by("-created_at")

        if report_start:
            bookings = bookings.filter(booking_date__gte=report_start)
            places = places.filter(created_at__gte=report_start)
            services = services.filter(created_at__gte=report_start)
            reviews = reviews.filter(created_at__gte=report_start)

        if filters["query"]:
            query = filters["query"]
            bookings = bookings.filter(
                Q(service__name__icontains=query) |
                Q(user__username__icontains=query) |
                Q(notes__icontains=query)
            )
            places = places.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(visiting_hours__icontains=query)
            )
            services = services.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(description__icontains=query) |
                Q(contact__icontains=query)
            )
            reviews = reviews.filter(
                Q(place__name__icontains=query) |
                Q(user__username__icontains=query) |
                Q(comment__icontains=query)
            )

        if filters["place_category"]:
            places = places.filter(category=filters["place_category"])
            reviews = reviews.filter(place__category=filters["place_category"])

        if filters["service_type"]:
            services = services.filter(type=filters["service_type"])
            bookings = bookings.filter(service__type=filters["service_type"])

        if filters["booking_status"]:
            bookings = bookings.filter(status=filters["booking_status"])

        min_rating = self._parse_float(filters["min_rating"], default=None)
        if min_rating is not None and filters["min_rating"] != "":
            places = places.filter(rating__gte=min_rating)
            services = services.filter(rating__gte=min_rating)
            reviews = reviews.filter(rating__gte=min_rating)

        if filters["has_image"] == "yes":
            places = places.exclude(images="")
            places = places.exclude(images__isnull=True)
        elif filters["has_image"] == "no":
            places = places.filter(Q(images="") | Q(images__isnull=True))

        return report_start, bookings, places, services, reviews

    def _build_report_preview_cards(self, places, services, reviews):
        place_cards = []
        for place in places[:8]:
            place_cards.append({
                "id": place.place_id,
                "name": place.name,
                "category": place.get_category_display(),
                "rating": round(place.rating, 1),
                "hours": place.visiting_hours,
                "image_url": self._safe_image_url(getattr(place, "images", None)),
                "description": place.description[:140],
            })

        service_cards = []
        for service in services[:6]:
            service_cards.append({
                "id": service.service_id,
                "name": service.name,
                "type": service.get_type_display(),
                "rating": round(service.rating, 1),
                "contact": service.contact,
                "address": service.address[:90],
            })

        review_cards = []
        for review in reviews[:6]:
            review_cards.append({
                "place": review.place.name,
                "user": review.user.username,
                "rating": review.rating,
                "comment": review.comment[:160],
            })

        return place_cards, service_cards, review_cards

    def _build_app_header_context(self, request, title):
        quick_links = [
            {"label": "Add Place", "url": "/admin/tourism/touristplace/add/", "icon": "fas fa-plus"},
            {"label": "Bookings", "url": "/admin/tourism/booking/", "icon": "fas fa-calendar-check"},
            {"label": "Reports", "url": "/admin/reports/", "icon": "fas fa-chart-column"},
            {"label": "Website", "url": "/", "icon": "fas fa-arrow-up-right-from-square"},
        ]
        return {
            "app_header_title": title,
            "app_header_subtitle": "Mathura tourism operations, content, and support controls.",
            "app_header_quick_links": quick_links,
            "app_header_active_path": request.path,
            "app_header_user_initial": (request.user.username[:1] if request.user.is_authenticated else "A").upper(),
        }

    def _build_dashboard_context(self):
        """Build shared dashboard and reporting context."""
        last_week = timezone.now() - timedelta(days=7)
        report_window = timedelta(days=30)
        report_start = timezone.now() - report_window if report_window else None

        total_places = TouristPlace.objects.count()
        total_users = UserProfile.objects.count()
        total_reviews = Review.objects.count()
        total_services = LocalService.objects.count()
        total_bookings = Booking.objects.count()
        total_favorites = FavouritePlace.objects.count()
        total_temples = TempleGuide.objects.count()
        total_chat_sessions = ChatHistory.objects.count()

        recent_bookings = Booking.objects.filter(booking_date__gte=last_week).count()
        recent_reviews = Review.objects.filter(created_at__gte=last_week).count()
        new_users = UserProfile.objects.filter(created_at__gte=last_week).count()

        top_places = TouristPlace.objects.order_by('-rating', 'name')[:5]
        dashboard_places = (
            TouristPlace.objects
            .exclude(location_lat=0)
            .exclude(location_lng=0)
            .annotate(
                review_count=Count('reviews', distinct=True),
                favorite_count=Count('favourited_by', distinct=True),
            )
            .order_by('-rating', 'name')[:8]
        )
        top_services = LocalService.objects.order_by('-rating', 'name')[:5]

        recent_booking_items = Booking.objects.select_related('service', 'user').order_by('-booking_date')[:6]
        recent_review_items = Review.objects.select_related('place', 'user').order_by('-created_at')[:6]
        recent_chat_items = ChatHistory.objects.select_related('user').order_by('-created_at')[:6]

        trend_labels = []
        booking_trend = []
        review_trend = []
        user_trend = []
        for index in range(3, -1, -1):
            period_end = timezone.now() - timedelta(days=index * 7)
            period_start = period_end - timedelta(days=7)
            trend_labels.append(period_start.strftime("%d %b"))
            booking_trend.append(Booking.objects.filter(booking_date__gte=period_start, booking_date__lt=period_end).count())
            review_trend.append(Review.objects.filter(created_at__gte=period_start, created_at__lt=period_end).count())
            user_trend.append(UserProfile.objects.filter(created_at__gte=period_start, created_at__lt=period_end).count())

        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        completed_bookings = Booking.objects.filter(status='completed').count()
        cancelled_bookings = Booking.objects.filter(status='cancelled').count()

        unread_notifications = Notification.objects.filter(is_read=False).count()

        place_categories = list(
            TouristPlace.objects.values('category').annotate(count=Count('place_id')).order_by('-count', 'category')[:6]
        )
        service_types = list(
            LocalService.objects.values('type').annotate(count=Count('service_id')).order_by('-count', 'type')
        )

        avg_place_rating = TouristPlace.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        avg_service_rating = LocalService.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        avg_review_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0

        featured_places = []
        for place in dashboard_places:
            rush_level, rush_score = self._get_rush_level(
                getattr(place, "review_count", 0),
                getattr(place, "favorite_count", 0),
                place.rating,
            )
            featured_places.append({
                "id": place.place_id,
                "name": place.name,
                "category_key": place.category,
                "category": place.get_category_display(),
                "rating": round(place.rating, 1),
                "visiting_hours": place.visiting_hours,
                "lat": place.location_lat,
                "lng": place.location_lng,
                "image_url": self._safe_image_url(getattr(place, "images", None)),
                "distance_label": f"{place.location_lat:.3f}, {place.location_lng:.3f}",
                "description": place.description[:150],
                "review_count": getattr(place, "review_count", 0),
                "favorite_count": getattr(place, "favorite_count", 0),
                "rush_level": rush_level,
                "rush_score": round(rush_score, 1),
                "is_temple": place.category == "temple",
            })

        map_points = []
        for index, place in enumerate(featured_places, start=1):
            map_points.append({
                "id": place["id"],
                "name": place["name"],
                "category_key": place["category_key"],
                "category": place["category"],
                "lat": place["lat"],
                "lng": place["lng"],
                "visiting_hours": place["visiting_hours"],
                "weight": max(place["rush_score"], 1),
                "stop": index,
                "rating": place["rating"],
                "review_count": place["review_count"],
                "favorite_count": place["favorite_count"],
                "rush_level": place["rush_level"],
                "rush_score": place["rush_score"],
                "is_temple": place["is_temple"],
                "marker_type": "temple" if place["is_temple"] else "place",
            })

        route_segments = []
        if len(map_points) > 1:
            for left, right in zip(map_points, map_points[1:]):
                route_segments.append({
                    "from": left["name"],
                    "to": right["name"],
                    "points": [[left["lat"], left["lng"]], [right["lat"], right["lng"]]],
                })

        rush_summary = sorted(
            [
                {
                    "id": place["id"],
                    "name": place["name"],
                    "rush_level": place["rush_level"],
                    "rush_score": place["rush_score"],
                    "review_count": place["review_count"],
                    "favorite_count": place["favorite_count"],
                }
                for place in featured_places
            ],
            key=lambda item: item["rush_score"],
            reverse=True,
        )

        default_map_filter = "temple" if any(item["category"] == "temple" for item in place_categories) else "all"

        booking_queryset = Booking.objects.select_related("service", "user").order_by("-booking_date")
        review_queryset = Review.objects.select_related("place", "user").order_by("-created_at")
        service_queryset = LocalService.objects.order_by("-rating", "name")
        place_queryset = TouristPlace.objects.order_by("-rating", "name")
        if report_start:
            booking_queryset = booking_queryset.filter(booking_date__gte=report_start)
            review_queryset = review_queryset.filter(created_at__gte=report_start)
            place_queryset = place_queryset.filter(created_at__gte=report_start)
            service_queryset = service_queryset.filter(created_at__gte=report_start)

        return {
            'title': 'Dashboard',
            'total_places': total_places,
            'total_users': total_users,
            'total_reviews': total_reviews,
            'total_services': total_services,
            'total_bookings': total_bookings,
            'total_favorites': total_favorites,
            'total_temples': total_temples,
            'total_chat_sessions': total_chat_sessions,
            'recent_bookings': recent_bookings,
            'recent_reviews': recent_reviews,
            'new_users': new_users,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'unread_notifications': unread_notifications,
            'top_places': top_places,
            'top_services': top_services,
            'place_categories': place_categories,
            'service_types': service_types,
            'recent_booking_items': recent_booking_items,
            'recent_review_items': recent_review_items,
            'recent_chat_items': recent_chat_items,
            'avg_place_rating': round(avg_place_rating, 1),
            'avg_service_rating': round(avg_service_rating, 1),
            'avg_review_rating': round(avg_review_rating, 1),
            'featured_places': featured_places,
            'rush_summary': rush_summary,
            'has_map_points': bool(map_points),
            'default_map_filter': default_map_filter,
            'dashboard_map_filters': [
                {"value": "all", "label": "All"},
                *[
                    {"value": item["category"], "label": item["category"].title()}
                    for item in place_categories
                ],
            ],
            'trend_labels_json': json.dumps(trend_labels),
            'booking_trend_json': json.dumps(booking_trend),
            'review_trend_json': json.dumps(review_trend),
            'user_trend_json': json.dumps(user_trend),
            'place_categories_json': json.dumps([
                {'label': item['category'].title(), 'value': item['count']} for item in place_categories
            ]),
            'booking_status_json': json.dumps([
                {'label': 'Pending', 'value': pending_bookings},
                {'label': 'Confirmed', 'value': confirmed_bookings},
                {'label': 'Completed', 'value': completed_bookings},
                {'label': 'Cancelled', 'value': cancelled_bookings},
            ]),
            'map_places_json': json.dumps(map_points),
            'map_routes_json': json.dumps(route_segments),
            'map_heat_json': json.dumps([[item["lat"], item["lng"], item["weight"]] for item in map_points]),
            'report_window': '30d',
            'report_scope': 'bookings',
            'report_rows': booking_queryset[:12],
            'report_place_rows': place_queryset[:12],
            'report_service_rows': service_queryset[:12],
            'report_review_rows': review_queryset[:12],
            **self._report_filter_options(),
        }

    @staticmethod
    def _get_report_window_value(request):
        return request.GET.get("window", "30d")

    @staticmethod
    def _get_report_scope_value(request):
        return request.GET.get("scope", "bookings")

    def admin_site_dashboard(self, request):
        """Custom dashboard view"""
        context = {
            **self.each_context(request),
            **self._build_dashboard_context(),
        }
        context.update(self._build_app_header_context(request, "Dashboard"))
        return render(request, 'admin/dashboard.html', context)

    def admin_reports(self, request):
        """Reporting page for admin users."""
        context = {
            **self.each_context(request),
            **self._build_dashboard_context(),
        }
        context['title'] = 'Reports'
        filters = self._get_report_filters(request)
        scope = filters["scope"]
        window = filters["window"]
        report_start, bookings, places, services, reviews = self._apply_report_filters(filters)

        if request.GET.get("export") == "csv":
            return self._export_report_csv(scope, bookings, places, services, reviews)

        place_preview_cards, service_preview_cards, review_preview_cards = self._build_report_preview_cards(
            places, services, reviews
        )

        context.update({
            "report_window": window,
            "report_scope": scope,
            "report_query": filters["query"],
            "report_place_category": filters["place_category"],
            "report_service_type": filters["service_type"],
            "report_booking_status": filters["booking_status"],
            "report_min_rating": filters["min_rating"],
            "report_has_image": filters["has_image"],
            "report_rows": bookings[:12],
            "report_place_rows": places[:12],
            "report_service_rows": services[:12],
            "report_review_rows": reviews[:12],
            "report_generated_at": timezone.now(),
            "report_range_label": "All time" if report_start is None else f"Since {report_start:%d %b %Y}",
            "report_place_cards": place_preview_cards,
            "report_service_cards": service_preview_cards,
            "report_review_cards": review_preview_cards,
            **self._build_app_header_context(request, "Reports"),
        })
        return render(request, 'admin/reports.html', context)

    def admin_reports_print(self, request):
        """Printable report view for browser print/PDF."""
        context = {
            **self.each_context(request),
            **self._build_dashboard_context(),
        }
        context["title"] = "Printable Reports"
        filters = self._get_report_filters(request)
        window = filters["window"]
        scope = filters["scope"]
        report_start, bookings, places, services, reviews = self._apply_report_filters(filters)
        place_preview_cards, service_preview_cards, review_preview_cards = self._build_report_preview_cards(
            places, services, reviews
        )

        context.update({
            "report_window": window,
            "report_scope": scope,
            "report_rows": bookings[:50],
            "report_place_rows": places[:50],
            "report_service_rows": services[:50],
            "report_review_rows": reviews[:50],
            "report_generated_at": timezone.now(),
            "report_range_label": "All time" if report_start is None else f"Since {report_start:%d %b %Y}",
            "report_query": filters["query"],
            "report_place_category": filters["place_category"],
            "report_service_type": filters["service_type"],
            "report_booking_status": filters["booking_status"],
            "report_min_rating": filters["min_rating"],
            "report_has_image": filters["has_image"],
            "report_place_cards": place_preview_cards,
            "report_service_cards": service_preview_cards,
            "report_review_cards": review_preview_cards,
        })
        return render(request, "admin/reports_print.html", context)

    def _export_report_csv(self, scope, bookings, places, services, reviews):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{scope}-report.csv"'
        writer = csv.writer(response)

        if scope == "places":
            writer.writerow(["Place ID", "Name", "Category", "Rating", "Visiting Hours", "Created At"])
            for place in places:
                writer.writerow([place.place_id, place.name, place.get_category_display(), place.rating, place.visiting_hours, place.created_at])
        elif scope == "services":
            writer.writerow(["Service ID", "Name", "Type", "Rating", "Contact", "Created At"])
            for service in services:
                writer.writerow([service.service_id, service.name, service.get_type_display(), service.rating, service.contact, service.created_at])
        elif scope == "reviews":
            writer.writerow(["Place", "User", "Rating", "Comment", "Created At"])
            for review in reviews:
                writer.writerow([review.place.name, review.user.username, review.rating, review.comment, review.created_at])
        else:
            writer.writerow(["Booking ID", "Service", "User", "Status", "Guests", "Booked At"])
            for booking in bookings:
                writer.writerow([booking.id, booking.service.name, booking.user.username, booking.get_status_display(), booking.number_of_guests, booking.booking_date])

        return response
    
    def index(self, request, extra_context=None):
        """Override index to redirect to dashboard"""
        extra_context = extra_context or {}
        return self.admin_site_dashboard(request)


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='admin')
