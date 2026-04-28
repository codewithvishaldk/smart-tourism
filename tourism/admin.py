from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.db import models
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .custom_admin import custom_admin_site
from .models import (
    Booking,
    ChatHistory,
    FavouritePlace,
    LocalService,
    Notification,
    Review,
    TempleGuide,
    TouristPlace,
    TripPlan,
    UserProfile,
)


class UserProfileResource(resources.ModelResource):
    class Meta:
        model = UserProfile
        fields = ("id", "user__username", "user__email", "phone", "created_at", "updated_at")


class TouristPlaceResource(resources.ModelResource):
    class Meta:
        model = TouristPlace
        fields = ("place_id", "name", "category", "rating", "visiting_hours", "created_at")


class BookingResource(resources.ModelResource):
    class Meta:
        model = Booking
        fields = ("id", "service__name", "user__username", "status", "booking_date", "scheduled_date")


class TempleGuideResource(resources.ModelResource):
    class Meta:
        model = TempleGuide
        fields = ("id", "name", "region", "category", "main_deity", "crowd_level", "updated_at")


class PremiumAdminMixin:
    save_on_top = True
    list_per_page = 20
    list_max_show_all = 200
    formfield_overrides = {
        models.TextField: {"widget": admin.widgets.AdminTextareaWidget(attrs={"rows": 5})},
        models.JSONField: {"widget": admin.widgets.AdminTextareaWidget(attrs={"rows": 6})},
    }

    @staticmethod
    def _change_url(obj):
        return reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk])

    @staticmethod
    def _changelist_url(model):
        return reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist")

    @staticmethod
    def _button(url, label, tone=""):
        tone_class = f" admin-table-action--{tone}" if tone else ""
        return format_html('<a class="admin-table-action{}" href="{}">{}</a>', tone_class, url, label)

    def _buttons(self, *buttons):
        items = [button for button in buttons if button]
        if not items:
            return "-"
        return format_html(
            '<div class="admin-action-stack">{}</div>',
            format_html_join("", "{}", ((item,) for item in items)),
        )

    @staticmethod
    def _live_place_url(place):
        return f"/place/{place.place_id}/"

    def _place_reviews_url(self, place):
        return f"{self._changelist_url(Review)}?place__place_id__exact={place.place_id}"

    def _service_bookings_url(self, service):
        return f"{self._changelist_url(Booking)}?service__service_id__exact={service.service_id}"

    def _user_bookings_url(self, user):
        return f"{self._changelist_url(Booking)}?user__id__exact={user.id}"

    @staticmethod
    def _thumb_image(url, alt):
        return format_html('<img src="{}" alt="{}" class="admin-list-thumb">', url, alt)

    @staticmethod
    def _thumb_icon(label, sublabel, tone="indigo"):
        return format_html(
            '<div class="admin-list-thumb admin-list-thumb--icon admin-list-thumb--{}"><strong>{}</strong><span>{}</span></div>',
            tone,
            label,
            sublabel,
        )

    def _place_thumb(self, place):
        image = getattr(place, "images", None)
        if image:
            try:
                return self._thumb_image(image.url, place.name)
            except Exception:
                pass
        return self._thumb_icon(place.name[:2].upper(), place.get_category_display()[:10], "indigo")


class UserProfileAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    resource_class = UserProfileResource
    list_display = ("profile_thumb", "user", "phone", "created_at", "user_link", "profile_actions")
    search_fields = ("user__username", "user__email", "phone")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at", "user_link")

    fieldsets = (
        ("User", {"fields": ("user", "user_link")}),
        ("Contact", {"fields": ("phone", "preferences")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def profile_thumb(self, obj):
        return self._thumb_icon((obj.user.username[:1] or "U").upper(), "Profile", "teal")

    profile_thumb.short_description = ""

    def user_link(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.user_id, obj.user.get_full_name() or obj.user.username)

    user_link.short_description = "Open User"

    def profile_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Edit", "primary"),
            self._button(f"/admin/auth/user/{obj.user_id}/change/", "User", "accent"),
            self._button(self._user_bookings_url(obj.user), "Bookings"),
        )

    profile_actions.short_description = "Quick Actions"


class TouristPlaceAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    resource_class = TouristPlaceResource
    list_display = ("place_thumb", "name", "category_badge", "rating_display", "visiting_hours", "review_count", "place_actions")
    list_filter = ("category", "rating", "created_at")
    search_fields = ("name", "description")
    readonly_fields = (
        "rating",
        "created_at",
        "updated_at",
        "review_count",
        "image_preview",
        "place_snapshot",
        "place_action_panel",
    )
    ordering = ("-rating", "name")

    fieldsets = (
        ("Place", {"fields": ("name", "category", "description", "images", "image_preview")}),
        ("Coordinates", {"fields": ("location_lat", "location_lng")}),
        ("Visit Info", {"fields": ("visiting_hours",)}),
        ("Preview", {"fields": ("place_snapshot", "place_action_panel"), "classes": ("wide",)}),
        ("Metrics", {"fields": ("rating", "review_count"), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def place_thumb(self, obj):
        return self._place_thumb(obj)

    place_thumb.short_description = ""

    def category_badge(self, obj):
        palette = {"temple": "#8b5cf6", "ghat": "#0f766e", "museum": "#2563eb", "park": "#15803d", "other": "#6b7280"}
        color = palette.get(obj.category, "#6b7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:4px 10px;border-radius:999px;font-size:12px;">{}</span>',
            color,
            obj.get_category_display(),
        )

    category_badge.short_description = "Category"
    category_badge.admin_order_field = "category"

    def rating_display(self, obj):
        color = "#15803d" if obj.rating >= 4 else "#b45309" if obj.rating >= 3 else "#b91c1c"
        return format_html('<span style="color:{};font-weight:700;">&#9733; {}</span>', color, f"{obj.rating:.1f}")

    rating_display.short_description = "Rating"
    rating_display.admin_order_field = "rating"

    def review_count(self, obj):
        return obj.reviews.count()

    review_count.short_description = "Reviews"

    def place_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Edit", "primary"),
            self._button(self._live_place_url(obj), "Open", "accent"),
            self._button(self._place_reviews_url(obj), "Reviews"),
        )

    place_actions.short_description = "Quick Actions"

    def image_preview(self, obj):
        if getattr(obj, "images", None):
            return format_html(
                '<div class="admin-preview-card"><img src="{}" alt="{}" style="max-width:240px;border-radius:14px;"></div>',
                obj.images.url,
                obj.name,
            )
        return "No image uploaded"

    image_preview.short_description = "Image Preview"

    def place_snapshot(self, obj):
        if not obj.pk:
            return "Save the place to see a premium preview card."
        return format_html(
            '<div class="admin-preview-card"><strong>{}</strong><div>Category: {}</div><div>Coordinates: {}, {}</div><div>Hours: {}</div><div>Reviews: {}</div></div>',
            obj.name,
            obj.get_category_display(),
            f"{obj.location_lat:.4f}",
            f"{obj.location_lng:.4f}",
            obj.visiting_hours or "Not set",
            obj.reviews.count(),
        )

    place_snapshot.short_description = "Place Snapshot"

    def place_action_panel(self, obj):
        if not obj.pk:
            return "Save the place to unlock live preview actions."
        return format_html(
            '<div class="admin-preview-card admin-preview-card--soft"><strong>Quick Actions</strong>{}</div>',
            self._buttons(
                self._button(self._live_place_url(obj), "Open Live Page", "accent"),
                self._button(self._place_reviews_url(obj), "Open Reviews"),
                self._button(f"/admin/reports/?scope=places&query={obj.name}", "Search in Reports"),
            ),
        )

    place_action_panel.short_description = "Action Panel"


class ReviewAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    list_display = ("review_thumb", "place", "user", "rating_stars", "created_at", "approved_status", "review_actions")
    list_filter = ("rating", "created_at", "place__category")
    search_fields = ("place__name", "user__username", "comment")
    readonly_fields = ("created_at", "updated_at", "user_summary")
    ordering = ("-created_at",)

    fieldsets = (
        ("Review", {"fields": ("place", "user", "user_summary")}),
        ("Content", {"fields": ("rating", "comment")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def review_thumb(self, obj):
        return self._place_thumb(obj.place)

    review_thumb.short_description = ""

    def rating_stars(self, obj):
        stars = ("★" * int(obj.rating)) + ("☆" * (5 - int(obj.rating)))
        color = "#15803d" if obj.rating >= 4 else "#b45309" if obj.rating >= 3 else "#b91c1c"
        return format_html('<span style="color:{};font-size:15px;">{}</span>', color, stars)

    rating_stars.short_description = "Rating"
    rating_stars.admin_order_field = "rating"

    def approved_status(self, _obj):
        return format_html('<span style="background:#dcfce7;color:#166534;padding:4px 10px;border-radius:999px;font-size:12px;">Visible</span>')

    approved_status.short_description = "Status"

    def user_summary(self, obj):
        return format_html("<strong>{}</strong><br>{}", obj.user.get_full_name() or obj.user.username, obj.user.email or "No email")

    user_summary.short_description = "User"

    def review_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Edit", "primary"),
            self._button(self._live_place_url(obj.place), "Place", "accent"),
            self._button(f"/admin/auth/user/{obj.user_id}/change/", "User"),
        )

    review_actions.short_description = "Quick Actions"


class LocalServiceAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    list_display = ("service_thumb", "name", "service_type", "contact_display", "rating_display", "location_summary", "service_actions")
    list_filter = ("type", "rating", "created_at")
    search_fields = ("name", "address", "contact", "description")
    readonly_fields = ("created_at", "updated_at", "service_snapshot", "service_action_panel")

    fieldsets = (
        ("Service", {"fields": ("name", "type", "description")}),
        ("Contact", {"fields": ("contact", "address")}),
        ("Coordinates", {"fields": ("location_lat", "location_lng")}),
        ("Preview", {"fields": ("service_snapshot", "service_action_panel"), "classes": ("wide",)}),
        ("Metrics", {"fields": ("rating",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def service_thumb(self, obj):
        tone_map = {"hotel": "blue", "restaurant": "rose", "transport": "amber", "cafe": "green"}
        return self._thumb_icon(obj.name[:2].upper(), obj.get_type_display()[:10], tone_map.get(obj.type, "teal"))

    service_thumb.short_description = ""

    def service_type(self, obj):
        palette = {"hotel": "#2563eb", "restaurant": "#dc2626", "transport": "#d97706", "cafe": "#059669"}
        color = palette.get(obj.type, "#6b7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:4px 10px;border-radius:999px;font-size:12px;">{}</span>',
            color,
            obj.get_type_display(),
        )

    service_type.short_description = "Type"
    service_type.admin_order_field = "type"

    def contact_display(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.contact, obj.contact)

    contact_display.short_description = "Contact"

    def rating_display(self, obj):
        return format_html('<span style="font-weight:700;">&#9733; {}</span>', f"{obj.rating:.1f}")

    rating_display.short_description = "Rating"
    rating_display.admin_order_field = "rating"

    def location_summary(self, obj):
        return f"{obj.location_lat:.4f}, {obj.location_lng:.4f}"

    location_summary.short_description = "Coordinates"

    def service_snapshot(self, obj):
        if not obj.pk:
            return "Save the service to see a premium preview card."
        return format_html(
            '<div class="admin-preview-card"><strong>{}</strong><div>Type: {}</div><div>Contact: {}</div><div>Address: {}</div><div>Bookings: {}</div></div>',
            obj.name,
            obj.get_type_display(),
            obj.contact or "Not set",
            obj.address or "Not set",
            obj.bookings.count(),
        )

    service_snapshot.short_description = "Service Snapshot"

    def service_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Edit", "primary"),
            self._button(self._service_bookings_url(obj), "Bookings", "accent"),
            self._button(f"tel:{obj.contact}", "Call"),
        )

    service_actions.short_description = "Quick Actions"

    def service_action_panel(self, obj):
        if not obj.pk:
            return "Save the service to unlock linked actions."
        return format_html(
            '<div class="admin-preview-card admin-preview-card--soft"><strong>Quick Actions</strong>{}</div>',
            self._buttons(
                self._button(self._service_bookings_url(obj), "Open Service Bookings", "accent"),
                self._button(f"/admin/reports/?scope=services&query={obj.name}", "Search in Reports"),
            ),
        )

    service_action_panel.short_description = "Action Panel"


class BookingAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    resource_class = BookingResource
    list_display = ("booking_thumb", "booking_id", "service", "user", "status_badge", "booking_date", "guest_count", "booking_actions")
    list_filter = ("status", "booking_date", "scheduled_date")
    search_fields = ("service__name", "user__username", "id")
    readonly_fields = ("booking_date", "updated_at", "user_info", "service_info", "booking_summary", "linked_actions")

    fieldsets = (
        ("Booking", {"fields": ("service", "user", "user_info", "service_info")}),
        ("Schedule", {"fields": ("scheduled_date", "number_of_guests", "notes")}),
        ("Quick Actions", {"fields": ("booking_summary", "linked_actions"), "classes": ("wide",)}),
        ("Status", {"fields": ("status", "booking_date", "updated_at")}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<path:object_id>/confirm/", self.admin_site.admin_view(self.confirm_booking), name="tourism_booking_confirm"),
            path("<path:object_id>/complete/", self.admin_site.admin_view(self.complete_booking), name="tourism_booking_complete"),
            path("<path:object_id>/cancel/", self.admin_site.admin_view(self.cancel_booking), name="tourism_booking_cancel"),
        ]
        return custom_urls + urls

    def booking_thumb(self, obj):
        tone_map = {"pending": "amber", "confirmed": "blue", "completed": "green", "cancelled": "rose"}
        return self._thumb_icon(str(obj.id), obj.get_status_display()[:10], tone_map.get(obj.status, "teal"))

    booking_thumb.short_description = ""

    def booking_id(self, obj):
        return f"#{obj.id}"

    booking_id.short_description = "Booking"

    def status_badge(self, obj):
        palette = {
            "pending": ("#fef3c7", "#92400e"),
            "confirmed": ("#dbeafe", "#1d4ed8"),
            "completed": ("#dcfce7", "#166534"),
            "cancelled": ("#fee2e2", "#991b1b"),
        }
        bg, fg = palette.get(obj.status, ("#e5e7eb", "#374151"))
        return format_html(
            '<span style="background:{};color:{};padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700;">{}</span>',
            bg,
            fg,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def guest_count(self, obj):
        return obj.number_of_guests

    guest_count.short_description = "Guests"
    guest_count.admin_order_field = "number_of_guests"

    def user_info(self, obj):
        profile = getattr(obj.user, "profile", None)
        phone = profile.phone if profile and profile.phone else "N/A"
        return format_html("<strong>{}</strong><br>Email: {}<br>Phone: {}", obj.user.get_full_name() or obj.user.username, obj.user.email or "N/A", phone)

    user_info.short_description = "User Details"

    def service_info(self, obj):
        return format_html("<strong>{}</strong><br>Type: {}<br>Contact: {}", obj.service.name, obj.service.get_type_display(), obj.service.contact)

    service_info.short_description = "Service Details"

    def booking_actions(self, obj):
        buttons = [self._button(self._change_url(obj), "Edit", "primary")]
        if obj.status != "confirmed":
            buttons.append(self._button(reverse("admin:tourism_booking_confirm", args=[obj.pk]), "Confirm", "success"))
        if obj.status != "completed":
            buttons.append(self._button(reverse("admin:tourism_booking_complete", args=[obj.pk]), "Complete", "accent"))
        if obj.status != "cancelled":
            buttons.append(self._button(reverse("admin:tourism_booking_cancel", args=[obj.pk]), "Cancel", "danger"))
        return self._buttons(*buttons)

    booking_actions.short_description = "Actions"

    def booking_summary(self, obj):
        if not obj.pk:
            return "Save the booking to unlock quick actions."
        return format_html(
            '<div class="admin-preview-card"><strong>Quick Booking Actions</strong>{}</div>',
            self._buttons(
                self._button(reverse("admin:tourism_booking_confirm", args=[obj.pk]), "Confirm", "success"),
                self._button(reverse("admin:tourism_booking_complete", args=[obj.pk]), "Complete", "accent"),
                self._button(reverse("admin:tourism_booking_cancel", args=[obj.pk]), "Cancel", "danger"),
            ),
        )

    booking_summary.short_description = "Workflow"

    def linked_actions(self, obj):
        if not obj.pk:
            return "Save the booking to open linked records."
        return format_html(
            '<div class="admin-preview-card admin-preview-card--soft"><strong>Linked Records</strong>{}</div>',
            self._buttons(
                self._button(f"/admin/auth/user/{obj.user_id}/change/", "Open User"),
                self._button(f"/admin/tourism/localservice/{obj.service_id}/change/", "Open Service", "accent"),
            ),
        )

    linked_actions.short_description = "Linked Records"

    def _set_status(self, request, object_id, status_value, label):
        booking = self.get_object(request, object_id)
        if booking is None:
            self.message_user(request, "Booking not found.", level=messages.ERROR)
            return redirect(self._changelist_url(Booking))
        booking.status = status_value
        booking.save(update_fields=["status", "updated_at"])
        self.message_user(request, f"Booking #{booking.id} marked as {label}.", level=messages.SUCCESS)
        return redirect(request.META.get("HTTP_REFERER") or self._change_url(booking))

    def confirm_booking(self, request, object_id):
        return self._set_status(request, object_id, "confirmed", "confirmed")

    def complete_booking(self, request, object_id):
        return self._set_status(request, object_id, "completed", "completed")

    def cancel_booking(self, request, object_id):
        return self._set_status(request, object_id, "cancelled", "cancelled")


class NotificationAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    list_display = ("notification_thumb", "user", "short_message", "read_status", "date", "notification_actions")
    list_filter = ("is_read", "date")
    search_fields = ("user__username", "message")
    readonly_fields = ("date",)

    def notification_thumb(self, obj):
        return self._thumb_icon("NT", "Unread" if not obj.is_read else "Read", "rose" if not obj.is_read else "green")

    notification_thumb.short_description = ""

    def short_message(self, obj):
        return f"{obj.message[:60]}..." if len(obj.message) > 60 else obj.message

    short_message.short_description = "Message"

    def read_status(self, obj):
        if obj.is_read:
            return format_html('<span style="color:#166534;font-weight:700;">Read</span>')
        return format_html('<span style="color:#991b1b;font-weight:700;">Unread</span>')

    read_status.short_description = "Status"
    read_status.admin_order_field = "is_read"

    def notification_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Edit", "primary"),
            self._button(f"/admin/auth/user/{obj.user_id}/change/", "User"),
        )

    notification_actions.short_description = "Quick Actions"


class FavouritePlaceAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    list_display = ("favourite_thumb", "place", "user", "added_at", "favourite_count", "favourite_actions")
    list_filter = ("added_at",)
    search_fields = ("place__name", "user__username")
    readonly_fields = ("added_at", "favourite_count")

    def favourite_thumb(self, obj):
        return self._place_thumb(obj.place)

    favourite_thumb.short_description = ""

    def favourite_count(self, obj):
        return FavouritePlace.objects.filter(place=obj.place).count()

    favourite_count.short_description = "Saved By"

    def favourite_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Edit", "primary"),
            self._button(self._live_place_url(obj.place), "Open Place", "accent"),
            self._button(f"/admin/auth/user/{obj.user_id}/change/", "User"),
        )

    favourite_actions.short_description = "Quick Actions"


class ChatHistoryAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    list_display = ("chat_thumb", "user", "short_message", "model_name", "created_at", "message_length", "chat_actions")
    list_filter = ("created_at", "model_name")
    search_fields = ("user__username", "user_message", "assistant_response")
    readonly_fields = ("created_at", "full_user_message", "full_assistant_response", "weather_info", "finish_reason")

    fieldsets = (
        ("Chat", {"fields": ("user", "model_name", "finish_reason", "weather_info")}),
        ("Messages", {"fields": ("full_user_message", "full_assistant_response")}),
        ("Timestamp", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def chat_thumb(self, obj):
        return self._thumb_icon("AI", (obj.model_name or "Chat")[:10], "teal")

    chat_thumb.short_description = ""

    def short_message(self, obj):
        return f"{obj.user_message[:50]}..." if len(obj.user_message) > 50 else obj.user_message

    short_message.short_description = "User Message"

    def message_length(self, obj):
        return len(obj.user_message)

    message_length.short_description = "Length"

    def full_user_message(self, obj):
        return format_html('<div class="admin-preview-card">{}</div>', obj.user_message)

    full_user_message.short_description = "User Message"

    def full_assistant_response(self, obj):
        return format_html('<div class="admin-preview-card admin-preview-card--soft">{}</div>', obj.assistant_response)

    full_assistant_response.short_description = "Assistant Response"

    def chat_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Inspect", "primary"),
            self._button(f"/admin/auth/user/{obj.user_id}/change/", "User"),
        )

    chat_actions.short_description = "Quick Actions"


class TripPlanAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    list_display = ("trip_thumb", "trip_title", "user", "duration_display", "travelers_count", "budget_badge", "created_at", "trip_actions")
    list_filter = ("budget_style", "created_at")
    search_fields = ("trip_title", "user__username")
    readonly_fields = ("created_at", "updated_at", "trip_summary", "input_payload", "plan_payload")

    fieldsets = (
        ("Trip", {"fields": ("trip_title", "user")}),
        ("Details", {"fields": ("duration_days", "travelers", "budget_style")}),
        ("Planner Data", {"fields": ("input_payload", "plan_payload"), "classes": ("collapse",)}),
        ("Summary", {"fields": ("trip_summary", "raw_response")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def trip_thumb(self, obj):
        return self._thumb_icon(str(obj.duration_days), "Days", "blue")

    trip_thumb.short_description = ""

    def duration_display(self, obj):
        return f"{obj.duration_days} days"

    duration_display.short_description = "Duration"
    duration_display.admin_order_field = "duration_days"

    def travelers_count(self, obj):
        return obj.travelers

    travelers_count.short_description = "Travelers"
    travelers_count.admin_order_field = "travelers"

    def budget_badge(self, obj):
        palette = {
            "budget": ("#dcfce7", "#166534"),
            "balanced": ("#dbeafe", "#1d4ed8"),
            "moderate": ("#fef3c7", "#92400e"),
            "luxury": ("#fee2e2", "#991b1b"),
        }
        bg, fg = palette.get((obj.budget_style or "").lower(), ("#e5e7eb", "#374151"))
        return format_html(
            '<span style="background:{};color:{};padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700;">{}</span>',
            bg,
            fg,
            obj.budget_style or "N/A",
        )

    budget_badge.short_description = "Budget"
    budget_badge.admin_order_field = "budget_style"

    def trip_summary(self, obj):
        preview = obj.raw_response[:500] + "..." if len(obj.raw_response) > 500 else obj.raw_response
        return format_html('<div class="admin-preview-card" style="max-height:280px;overflow:auto;white-space:pre-wrap;">{}</div>', preview or "No summary available")

    trip_summary.short_description = "Trip Summary"

    def trip_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Edit", "primary"),
            self._button(f"/admin/auth/user/{obj.user_id}/change/", "User"),
            self._button(f"/admin/reports/?scope=bookings&query={obj.user.username}", "Related Reports"),
        )

    trip_actions.short_description = "Quick Actions"


class TempleGuideAdmin(PremiumAdminMixin, ImportExportModelAdmin):
    resource_class = TempleGuideResource
    list_display = ("guide_thumb", "name", "region_badge", "category_badge", "deity", "crowd_indicator", "updated_at", "guide_actions")
    list_filter = ("region", "category", "crowd_level", "updated_at")
    search_fields = ("name", "location_text", "main_deity", "google_map_keyword")
    readonly_fields = ("created_at", "updated_at", "location_info", "guide_preview", "visit_snapshot", "guide_action_panel")

    fieldsets = (
        ("Temple", {"fields": ("name", "main_deity", "category", "region", "location_text", "google_map_keyword")}),
        (
            "Visit Details",
            {
                "fields": (
                    "famous_for",
                    "history",
                    "best_time_to_visit",
                    "best_season",
                    "crowd_level",
                    "average_visit_duration",
                    "photography_policy",
                    "dress_code",
                    "entry_fee",
                    "vip_darshan",
                    "parking_info",
                )
            },
        ),
        ("Snapshot", {"fields": ("visit_snapshot", "guide_action_panel"), "classes": ("wide",)}),
        ("Structured Data", {"fields": ("timings", "important_tips", "aliases", "nearby_attractions", "local_market_food")}),
        ("Preview", {"fields": ("location_info", "guide_preview"), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def guide_thumb(self, obj):
        return self._thumb_icon(obj.name[:2].upper(), (obj.region or "Temple")[:10], "indigo")

    guide_thumb.short_description = ""

    def region_badge(self, obj):
        return format_html('<span style="background:#ede9fe;color:#5b21b6;padding:4px 10px;border-radius:999px;font-size:12px;">{}</span>', obj.region or "Unknown")

    region_badge.short_description = "Region"
    region_badge.admin_order_field = "region"

    def category_badge(self, obj):
        return format_html('<span style="background:#ecfeff;color:#155e75;padding:4px 10px;border-radius:999px;font-size:12px;">{}</span>', obj.category or "N/A")

    category_badge.short_description = "Category"
    category_badge.admin_order_field = "category"

    def deity(self, obj):
        return obj.main_deity or "N/A"

    deity.short_description = "Main Deity"
    deity.admin_order_field = "main_deity"

    def crowd_indicator(self, obj):
        palette = {"low": ("#dcfce7", "#166534"), "moderate": ("#fef3c7", "#92400e"), "high": ("#fee2e2", "#991b1b")}
        bg, fg = palette.get((obj.crowd_level or "").lower(), ("#e5e7eb", "#374151"))
        return format_html(
            '<span style="background:{};color:{};padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700;">{}</span>',
            bg,
            fg,
            obj.crowd_level or "Unknown",
        )

    crowd_indicator.short_description = "Crowd"
    crowd_indicator.admin_order_field = "crowd_level"

    def location_info(self, obj):
        return format_html("<strong>Region:</strong> {}<br><strong>Location:</strong> {}", obj.region or "N/A", obj.location_text or "N/A")

    location_info.short_description = "Location"

    def guide_preview(self, obj):
        parts = []
        if obj.famous_for:
            parts.append(f"Famous for: {obj.famous_for}")
        if obj.history:
            parts.append(f"History: {obj.history}")
        if obj.important_tips:
            parts.append("Tips: " + ", ".join(obj.important_tips))
        preview = "\n\n".join(parts) or "No preview available"
        short_preview = preview[:500] + "..." if len(preview) > 500 else preview
        return format_html('<div class="admin-preview-card" style="max-height:280px;overflow:auto;white-space:pre-wrap;">{}</div>', short_preview)

    guide_preview.short_description = "Guide Preview"

    def visit_snapshot(self, obj):
        if not obj.pk:
            return "Save the temple guide to see a premium preview card."
        return format_html(
            '<div class="admin-preview-card"><strong>{}</strong><div>Main deity: {}</div><div>Best time: {}</div><div>Entry fee: {}</div><div>Crowd level: {}</div></div>',
            obj.name,
            obj.main_deity or "Not set",
            obj.best_time_to_visit or "Not set",
            obj.entry_fee or "Not set",
            obj.crowd_level or "Not set",
        )

    visit_snapshot.short_description = "Visit Snapshot"

    def guide_actions(self, obj):
        return self._buttons(
            self._button(self._change_url(obj), "Edit", "primary"),
            self._button(f"/admin/tourism/touristplace/?q={obj.name}", "Match Place", "accent"),
            self._button(f"/admin/reports/?scope=places&query={obj.name}", "Report"),
        )

    guide_actions.short_description = "Quick Actions"

    def guide_action_panel(self, obj):
        if not obj.pk:
            return "Save the temple guide to unlock linked actions."
        return format_html(
            '<div class="admin-preview-card admin-preview-card--soft"><strong>Quick Actions</strong>{}</div>',
            self._buttons(
                self._button(f"/admin/tourism/touristplace/?q={obj.name}", "Search Matching Place", "accent"),
                self._button(f"/timetable-finder/?q={obj.name}", "Open Timetable Page"),
            ),
        )

    guide_action_panel.short_description = "Action Panel"


custom_admin_site.register(UserProfile, UserProfileAdmin)
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(TouristPlace, TouristPlaceAdmin)
custom_admin_site.register(Review, ReviewAdmin)
custom_admin_site.register(LocalService, LocalServiceAdmin)
custom_admin_site.register(Booking, BookingAdmin)
custom_admin_site.register(Notification, NotificationAdmin)
custom_admin_site.register(FavouritePlace, FavouritePlaceAdmin)
custom_admin_site.register(ChatHistory, ChatHistoryAdmin)
custom_admin_site.register(TripPlan, TripPlanAdmin)
custom_admin_site.register(TempleGuide, TempleGuideAdmin)
