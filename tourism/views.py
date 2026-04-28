from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
import json
import os
import re
import requests
from openrouter import OpenRouter
from .models import (
    TouristPlace, Review, LocalService, FavouritePlace,
    Notification, Booking, UserProfile, ChatHistory, TripPlan, TempleGuide
)
from .temple_guide_data import TEMPLE_GUIDE_DATA


class OpenRouterRequestError(Exception):
    """Raised when an OpenRouter request fails."""

    def __init__(self, message, status=500):
        super().__init__(message)
        self.status = status


def dashboard(request):
    """Dashboard view showing welcome and nearby places."""
    places = TouristPlace.objects.all()[:6]
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    else:
        notifications = []

    context = {
        'places': places,
        'notifications': notifications,
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)


def explore(request):
    """Explore all tourist places with filtering."""
    places = TouristPlace.objects.all()
    category = request.GET.get('category', '')

    if category:
        places = places.filter(category=category)

    search_query = request.GET.get('q', '')
    if search_query:
        places = places.filter(name__icontains=search_query)

    categories = TouristPlace.objects.values_list('category', flat=True).distinct()

    context = {
        'places': places,
        'categories': categories,
        'selected_category': category,
        'search_query': search_query,
    }
    return render(request, 'explore.html', context)


def normalize_lookup_key(value):
    """Normalize free-text keys for temple guide matching."""
    return re.sub(r'[^a-z0-9]+', '', value.lower()).strip()


def ensure_temple_guides_loaded():
    """Load bundled temple guide data if the table is empty."""
    if TempleGuide.objects.exists():
        return

    TempleGuide.objects.bulk_create(
        [TempleGuide(**item) for item in TEMPLE_GUIDE_DATA],
        ignore_conflicts=True,
    )


def get_matching_temple_guide(place_name):
    """Find the best matching temple guide for a place name."""
    if not place_name:
        return None

    ensure_temple_guides_loaded()
    normalized_target = normalize_lookup_key(place_name)
    for guide in TempleGuide.objects.all():
        if normalize_lookup_key(guide.name) == normalized_target:
            return guide
        for alias in guide.aliases or []:
            if normalize_lookup_key(alias) == normalized_target:
                return guide
    return None


def place_detail(request, place_id):
    """Detailed view of a tourist place."""
    place = get_object_or_404(TouristPlace, place_id=place_id)
    reviews = place.reviews.all()
    guide = get_matching_temple_guide(place.name)
    average_rating = 0
    if reviews.exists():
        average_rating = sum(r.rating for r in reviews) / reviews.count()

    is_favourite = False
    if request.user.is_authenticated:
        is_favourite = FavouritePlace.objects.filter(
            user=request.user, place=place
        ).exists()

    context = {
        'place': place,
        'reviews': reviews,
        'average_rating': average_rating,
        'is_favourite': is_favourite,
        'guide': guide,
    }
    return render(request, 'place_detail.html', context)


def navigation(request):
    """Full-page navigation with Google Maps."""
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    context = {
        'google_maps_api_key': google_maps_api_key,
    }
    return render(request, 'navigation.html', context)


def chatbot_page(request):
    """Chatbot interface page."""
    context = {}
    return render(request, 'chatbot.html', context)


def plan_trip_page(request):
    """AI trip planner and budget planner page."""
    context = {
        'focus_options': [
            'Temple darshan',
            'Vrindavan visit',
            'Yamuna ghats',
            'Family trip',
            'Budget travel',
            'Local food',
            'Festival vibes',
        ],
    }
    return render(request, 'plan_trip.html', context)


def rush_calculator_page(request):
    """Rush calculator page for estimating crowd levels."""
    context = {
        'places': TouristPlace.objects.order_by('name'),
        'days': [
            'Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday',
        ],
        'time_slots': [
            ('early_morning', 'Early Morning'),
            ('morning', 'Morning'),
            ('afternoon', 'Afternoon'),
            ('evening', 'Evening'),
            ('night', 'Night'),
        ],
        'special_events': [
            ('normal', 'Normal Day'),
            ('weekend', 'Weekend'),
            ('ekadashi', 'Ekadashi'),
            ('purnima', 'Purnima'),
            ('holi', 'Holi Season'),
            ('janmashtami', 'Janmashtami'),
            ('govardhan_puja', 'Govardhan Puja'),
        ],
    }
    return render(request, 'rush_calculator.html', context)


def timetable_finder_page(request):
    """Temple timetable and detail finder page."""
    ensure_temple_guides_loaded()
    guides = TempleGuide.objects.all().order_by('region', 'name')
    context = {
        'guides': guides,
        'regions': sorted({guide.region for guide in guides if guide.region}),
    }
    return render(request, 'timetable_finder.html', context)


def save_chat_history_for_user(request, user_message, assistant_response, weather_info='', model_name='', finish_reason=''):
    """Persist chat history for authenticated users."""
    if not request.user.is_authenticated:
        return

    ChatHistory.objects.create(
        user=request.user,
        user_message=user_message,
        assistant_response=assistant_response,
        weather_info=weather_info or '',
        model_name=model_name or '',
        finish_reason=finish_reason or '',
    )


def save_trip_plan_for_user(request, planner_input, plan_payload, raw_response, model_name='', finish_reason=''):
    """Persist AI trip plans for authenticated users."""
    if not request.user.is_authenticated:
        return

    trip_title = ''
    if isinstance(plan_payload, dict):
        trip_title = plan_payload.get('trip_title', '')

    TripPlan.objects.create(
        user=request.user,
        trip_title=trip_title or f"{planner_input.get('duration_days', 1)}-day Mathura plan",
        duration_days=planner_input.get('duration_days', 1),
        travelers=planner_input.get('travelers', 1),
        budget_style=planner_input.get('budget_style', ''),
        input_payload=planner_input,
        plan_payload=plan_payload if isinstance(plan_payload, dict) else {},
        raw_response=raw_response or '',
        model_name=model_name or '',
        finish_reason=finish_reason or '',
    )


def calculate_rush_estimate(place, visit_day, time_slot, special_event):
    """Estimate crowd rush using place type, time, day, and event signals."""
    category_weights = {
        'temple': 28,
        'ghat': 18,
        'museum': 8,
        'park': 10,
        'other': 12,
    }
    day_weights = {
        'Monday': 12,
        'Tuesday': 10,
        'Wednesday': 5,
        'Thursday': 8,
        'Friday': 11,
        'Saturday': 18,
        'Sunday': 20,
    }
    time_weights = {
        'early_morning': 8,
        'morning': 16,
        'afternoon': 6,
        'evening': 22,
        'night': 12,
    }
    event_weights = {
        'normal': 0,
        'weekend': 8,
        'ekadashi': 12,
        'purnima': 14,
        'holi': 30,
        'janmashtami': 35,
        'govardhan_puja': 24,
    }

    place_name = place.name.lower()
    place_bonus = 0
    place_factors = []

    if 'krishna janmabhoomi' in place_name:
        place_bonus += 18
        place_factors.append('Janmabhoomi par usually steady darshan crowd rehta hai.')
    if 'dwarkadhish' in place_name:
        place_bonus += 14
        place_factors.append('Dwarkadhish Mandir peak prayer hours mein zyada busy hota hai.')
    if 'vishram ghat' in place_name:
        place_bonus += 10
        place_factors.append('Vishram Ghat evening side par crowd badh sakta hai.')
    if 'prem mandir' in place_name:
        place_bonus += 16
        place_factors.append('Prem Mandir lighting hours mein footfall kaafi badhta hai.')
    if 'iskcon' in place_name:
        place_bonus += 12
        place_factors.append('ISKCON visits prayer timings aur weekends par fast increase karte hain.')

    score = (
        18
        + category_weights.get(place.category, 12)
        + day_weights.get(visit_day, 8)
        + time_weights.get(time_slot, 10)
        + event_weights.get(special_event, 0)
        + place_bonus
    )
    score = max(5, min(score, 100))

    if score <= 25:
        rush_level = 'Low'
        badge = 'success'
    elif score <= 50:
        rush_level = 'Moderate'
        badge = 'info'
    elif score <= 75:
        rush_level = 'High'
        badge = 'warning'
    else:
        rush_level = 'Very High'
        badge = 'danger'

    best_window = 'Weekday early morning ya afternoon slot best rahega.'
    if place.category == 'temple':
        best_window = 'Subah jaldi ya lunch ke baad ka slot usually better rahega.'
    elif place.category == 'ghat':
        best_window = 'Late morning ya afternoon mein relative crowd kam mil sakta hai.'

    avoid_window = 'Weekend evening aur major festival period avoid karna better rahega.'
    if special_event in ['holi', 'janmashtami', 'govardhan_puja']:
        avoid_window = 'Festival ke prime darshan hours mein crowd bahut intense ho sakta hai.'

    factors = [
        f'{place.get_category_display()} category naturally crowd attract karti hai.',
        f'{visit_day} ka expected footfall is estimate mein include hai.',
        f'{time_slot.replace("_", " ").title()} slot ka rush pattern score mein counted hai.',
    ]
    if special_event != 'normal':
        factors.append(f'{special_event.replace("_", " ").title()} ki wajah se extra rush consider kiya gaya hai.')
    factors.extend(place_factors)

    recommendations = [
        '10-20 minutes buffer lekar nikliye, especially temple area ke liye.',
        'Cash, water bottle aur simple footwear planning useful rahegi.',
        'Agar family ya elders saath hain, early slot prefer kariye.',
    ]
    if rush_level in ['High', 'Very High']:
        recommendations.append('Parking aur local e-rickshaw wait time zyada ho sakta hai.')
    if special_event in ['holi', 'janmashtami']:
        recommendations.append('Festival days par security checks aur queue time noticeably longer ho sakta hai.')

    summary = (
        f'{place.name} ke liye {visit_day} {time_slot.replace("_", " ")} slot mein '
        f'expected rush level {rush_level.lower()} se {("kaafi upar" if rush_level == "Very High" else "moderate to noticeable")}.'
    )

    return {
        'place_name': place.name,
        'rush_score': score,
        'rush_level': rush_level,
        'badge': badge,
        'summary': summary,
        'best_window': best_window,
        'avoid_window': avoid_window,
        'factors': factors,
        'recommendations': recommendations,
    }


def serialize_temple_guide(guide, mode='details'):
    """Serialize temple guide data for timetable/detail lookup."""
    payload = {
        'id': guide.id,
        'name': guide.name,
        'region': guide.region,
        'category': guide.category,
        'main_deity': guide.main_deity,
        'timings': guide.timings,
    }
    if mode == 'timetable':
        return payload

    payload.update({
        'location_text': guide.location_text,
        'famous_for': guide.famous_for,
        'history': guide.history,
        'best_time_to_visit': guide.best_time_to_visit,
        'best_season': guide.best_season,
        'crowd_level': guide.crowd_level,
        'average_visit_duration': guide.average_visit_duration,
        'photography_policy': guide.photography_policy,
        'dress_code': guide.dress_code,
        'entry_fee': guide.entry_fee,
        'vip_darshan': guide.vip_darshan,
        'nearby_attractions': guide.nearby_attractions,
        'parking_info': guide.parking_info,
        'google_map_keyword': guide.google_map_keyword,
        'local_market_food': guide.local_market_food,
        'important_tips': guide.important_tips,
    })
    return payload


def services(request):
    """Services page (hotels, restaurants, transport, cafes)."""
    service_type = request.GET.get('type', '')
    services_list = LocalService.objects.all()

    if service_type:
        services_list = services_list.filter(type=service_type)

    service_types = LocalService.objects.values_list('type', flat=True).distinct()

    context = {
        'services': services_list,
        'service_types': service_types,
        'selected_type': service_type,
    }
    return render(request, 'services.html', context)




@login_required
def favourites(request):
    """User's favourite places."""
    favourites = FavouritePlace.objects.filter(user=request.user)
    context = {
        'favourites': favourites,
    }
    return render(request, 'favourites.html', context)


@login_required
def profile(request):
    """User profile view."""
    profile = request.user.profile if hasattr(request.user, 'profile') else None
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        preferences = request.POST.get('preferences', '')
        if profile:
            profile.phone = phone
            profile.preferences = preferences
            profile.save()
        return redirect('profile')

    context = {
        'profile': profile,
        'recent_chat_histories': ChatHistory.objects.filter(user=request.user)[:8],
        'recent_trip_plans': TripPlan.objects.filter(user=request.user)[:8],
    }
    return render(request, 'profile.html', context)


def register(request):
    """User registration."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, 'register.html', {'error': "Passwords don't match"})

        if not username or not email or not password:
            return render(request, 'register.html', {'error': 'All fields are required'})

        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken'})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.get_or_create(user=user)
        login(request, user)
        return redirect('dashboard')

    return render(request, 'register.html')


def user_login(request):
    """User login."""
    next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            return render(request, 'login.html', {
                'error': 'Invalid credentials',
                'next': next_url,
            })

    return render(request, 'login.html', {'next': next_url})


def user_logout(request):
    """User logout."""
    logout(request)
    return redirect('dashboard')


def is_identity_query(message):
    """Check if the user is asking about the assistant's creator or model."""
    normalized = " ".join(message.lower().split())
    identity_phrases = [
        'who made you',
        'who created you',
        'who built you',
        'who developed you',
        'kisne banaya',
        'aapko kisne banaya',
        'tumhe kisne banaya',
        'developer kaun hai',
        'creator kaun hai',
        'owner kaun hai',
        'your developer',
        'your creator',
        'your owner',
        'developer',
        'creator',
        'created by',
        'made by',
        'built by',
        'developed by',
        'which model',
        'what model',
        'kaunsa model',
        'kaun sa model',
        'kaunse model',
        'kis model',
        'aap kis model par ho',
        'model are you using',
        'ai model',
        'llm',
        'openrouter model',
    ]
    return any(phrase in normalized for phrase in identity_phrases)


def build_identity_response(configured_model):
    """Return a consistent introduction for creator/model questions."""
    lines = [
        'Main Mathura Darshan Assistant hoon.',
        'Mathura Tourism by Sheetal.',
        'I am made by Sheetal Kashyap from Sanskriti University.',
    ]
    lines.append(
        'Main Mathura darshan, temples, ghats, food, hotels, festivals aur routes mein bhi help kar sakta hoon.'
    )
    return '\n'.join(lines)


def get_openrouter_models():
    """Return primary and fallback model list from environment."""
    primary_model = os.getenv(
        'OPENROUTER_MODEL',
        'google/gemma-3n-e4b-it:free'
    )
    fallback_models = os.getenv(
        'OPENROUTER_FALLBACK_MODELS',
        'google/gemma-3n-e2b-it:free,google/gemma-3-4b-it:free'
    )
    models_to_try = [primary_model]
    models_to_try.extend(
        model.strip() for model in fallback_models.split(',') if model.strip()
    )
    return primary_model, list(dict.fromkeys(models_to_try))


def normalize_message_content(content):
    """Normalize text or mixed OpenRouter content into displayable text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                if part.get('type') == 'text':
                    text_parts.append(part.get('text', ''))
                elif part.get('text'):
                    text_parts.append(part.get('text', ''))
        return '\n'.join(part for part in text_parts if part).strip()
    return str(content)


def send_openrouter_chat(messages, temperature=0.7, max_tokens=None):
    """Send a chat completion request to OpenRouter with fallback models."""
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
    if not openrouter_api_key:
        raise OpenRouterRequestError('OpenRouter API key not configured', status=500)

    _, models_to_try = get_openrouter_models()
    last_error = None

    for model in models_to_try:
        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens or int(os.getenv('OPENROUTER_MAX_TOKENS', '900')),
        }

        try:
            with OpenRouter(
                api_key=openrouter_api_key,
                http_referer='http://localhost:8000',
                x_open_router_title='Mathura Darshan',
                timeout_ms=12000,
            ) as client:
                result = client.chat.send(**payload)

            choice = result.choices[0]
            return {
                'content': normalize_message_content(choice.message.content),
                'finish_reason': getattr(choice, 'finish_reason', ''),
                'model': model,
            }

        except Exception as exc:
            status_code = getattr(exc, 'status_code', None) or getattr(exc, 'status', None) or 500
            error_message = str(exc) or f'OpenRouter API error: {status_code}'
            last_error = {
                'status': status_code,
                'message': error_message,
            }
            if status_code in [401, 403]:
                break

    if last_error and last_error['status'] == 429:
        raise OpenRouterRequestError(
            f"OpenRouter free models are rate limited right now. Details: {last_error['message']}",
            status=429,
        )

    raise OpenRouterRequestError(
        last_error['message'] if last_error else 'OpenRouter request failed',
        status=last_error['status'] if last_error else 500,
    )


def extract_json_from_text(text):
    """Extract a JSON object from raw model output."""
    if not text:
        return None

    fenced_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    candidates = []
    if fenced_match:
        candidates.append(fenced_match.group(1).strip())
    candidates.append(text.strip())

    decoder = json.JSONDecoder()
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        for index, char in enumerate(candidate):
            if char not in '{[':
                continue
            try:
                parsed, _ = decoder.raw_decode(candidate[index:])
                return parsed
            except json.JSONDecodeError:
                continue
    return None


def parse_rupee_amount(value):
    """Convert rupee-like values into integers."""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        digits = re.sub(r'[^0-9]', '', value)
        if digits:
            return int(digits)
    return 0


def get_trip_planner_context():
    """Build compact local context for the AI planner."""
    top_places = TouristPlace.objects.order_by('-rating', 'name')[:8]
    top_services = LocalService.objects.order_by('-rating', 'name')[:8]

    place_lines = [
        f"- {place.name} ({place.category}) | rating {place.rating:.1f} | hours {place.visiting_hours}"
        for place in top_places
    ]
    service_lines = [
        f"- {service.name} ({service.type}) | rating {service.rating:.1f} | {service.address}"
        for service in top_services
    ]

    return (
        "Suggested local places:\n"
        + ("\n".join(place_lines) if place_lines else "- Use well-known Mathura darshan places.")
        + "\n\nSuggested local services:\n"
        + ("\n".join(service_lines) if service_lines else "- Use realistic local transport, food, and stay options.")
    )


def normalize_budget_plan(plan_data, travelers):
    """Normalize planner output so frontend rendering stays stable."""
    budget_breakdown = plan_data.get('budget_breakdown', {})
    total_breakdown = 0

    if isinstance(budget_breakdown, dict):
        for key, item in budget_breakdown.items():
            if isinstance(item, dict):
                amount = parse_rupee_amount(item.get('amount', 0))
                item['amount'] = amount
                total_breakdown += amount

    daily_plan = plan_data.get('daily_plan', [])
    if isinstance(daily_plan, list):
        for index, item in enumerate(daily_plan, start=1):
            if isinstance(item, dict):
                item['day'] = parse_rupee_amount(item.get('day', index)) or index
                item['estimated_day_budget'] = parse_rupee_amount(item.get('estimated_day_budget', 0))

    totals = plan_data.get('total_estimated', {})
    total_min = total_breakdown
    total_max = total_breakdown
    total_note = ''
    if isinstance(totals, dict):
        total_min = parse_rupee_amount(totals.get('min', total_breakdown)) or total_breakdown
        total_max = parse_rupee_amount(totals.get('max', total_breakdown)) or total_breakdown
        total_note = totals.get('note', '')

    if total_min > total_max:
        total_min, total_max = total_max, total_min

    plan_data['budget_breakdown'] = budget_breakdown
    plan_data['daily_plan'] = daily_plan if isinstance(daily_plan, list) else []
    plan_data['money_saving_tips'] = plan_data.get('money_saving_tips', [])
    plan_data['booking_checklist'] = plan_data.get('booking_checklist', [])
    plan_data['total_estimated'] = {
        'min': total_min,
        'max': total_max,
        'note': total_note,
    }
    plan_data['estimated_per_person'] = int(total_max / max(1, travelers))
    return plan_data


@csrf_exempt
@require_http_methods(["POST"])
def plan_trip_api(request):
    """AI itinerary and budget planner endpoint."""
    try:
        data = json.loads(request.body)
        travelers = max(1, int(data.get('travelers', 1)))
        duration_days = max(1, min(7, int(data.get('duration_days', 2))))
        budget_style = data.get('budget_style', 'balanced').strip() or 'balanced'
        stay_preference = data.get('stay_preference', 'budget hotel').strip() or 'budget hotel'
        food_preference = data.get('food_preference', 'vegetarian').strip() or 'vegetarian'
        transport_preference = data.get('transport_preference', 'auto/e-rickshaw').strip() or 'auto/e-rickshaw'
        focus_areas = data.get('focus_areas', '').strip()
        notes = data.get('notes', '').strip()
        language = data.get('language', 'hinglish').strip() or 'hinglish'
        include_vrindavan = bool(data.get('include_vrindavan'))
        planner_input = {
            'duration_days': duration_days,
            'travelers': travelers,
            'budget_style': budget_style,
            'stay_preference': stay_preference,
            'food_preference': food_preference,
            'transport_preference': transport_preference,
            'focus_areas': focus_areas,
            'notes': notes,
            'language': language,
            'include_vrindavan': include_vrindavan,
        }

        planner_context = get_trip_planner_context()
        system_prompt = (
            "You are Mathura Tourism by Sheetal, an AI trip planner for Mathura and Vrindavan. "
            "Create realistic, useful, and budget-aware travel plans for Indian travelers. "
            "Reply in strict JSON only, without markdown or code fences. "
            "Use INR as the currency. "
            "Recommend sensible darshan timing, temple-first routing, realistic local transport, vegetarian food options, and clear saving tips. "
            "Use the user's requested language tone inside string values. "
            "Do not mention technical model names. "
            "If exact prices or timings can vary, keep estimates realistic and mention local confirmation in notes."
        )

        user_prompt = (
            f"Build a {duration_days}-day Mathura trip with budget planning.\n"
            f"Travelers: {travelers}\n"
            f"Budget style: {budget_style}\n"
            f"Stay preference: {stay_preference}\n"
            f"Food preference: {food_preference}\n"
            f"Transport preference: {transport_preference}\n"
            f"Include Vrindavan: {'yes' if include_vrindavan else 'no'}\n"
            f"Focus areas: {focus_areas or 'temples, local darshan, simple travel'}\n"
            f"Special notes: {notes or 'No special notes'}\n"
            f"Language style: {language}\n\n"
            f"{planner_context}\n\n"
            "Return JSON with this exact structure:\n"
            "{"
            "\"trip_title\":\"...\","
            "\"summary\":\"...\","
            "\"best_time_note\":\"...\","
            "\"budget_currency\":\"INR\","
            "\"budget_breakdown\":{"
            "\"stay\":{\"amount\":0,\"note\":\"...\"},"
            "\"food\":{\"amount\":0,\"note\":\"...\"},"
            "\"local_transport\":{\"amount\":0,\"note\":\"...\"},"
            "\"darshan_misc\":{\"amount\":0,\"note\":\"...\"},"
            "\"shopping_buffer\":{\"amount\":0,\"note\":\"...\"}"
            "},"
            "\"total_estimated\":{\"min\":0,\"max\":0,\"note\":\"...\"},"
            "\"daily_plan\":["
            "{"
            "\"day\":1,"
            "\"theme\":\"...\","
            "\"places\":[\"...\"],"
            "\"food\":\"...\","
            "\"transport\":\"...\","
            "\"estimated_day_budget\":0,"
            "\"notes\":\"...\""
            "}"
            "],"
            "\"money_saving_tips\":[\"...\"],"
            "\"booking_checklist\":[\"...\"]"
            "}"
        )

        combined_prompt = f"{system_prompt}\n\nUser trip request:\n{user_prompt}"
        ai_result = send_openrouter_chat(
            messages=[
                {'role': 'user', 'content': combined_prompt},
            ],
            temperature=0.5,
            max_tokens=1400,
        )

        plan_data = extract_json_from_text(ai_result['content'])
        if isinstance(plan_data, dict):
            normalized_plan = normalize_budget_plan(plan_data, travelers)
            save_trip_plan_for_user(
                request,
                planner_input=planner_input,
                plan_payload=normalized_plan,
                raw_response=ai_result['content'],
                model_name=ai_result['model'],
                finish_reason=ai_result['finish_reason'],
            )
            return JsonResponse({
                'success': True,
                'structured': True,
                'plan': normalized_plan,
                'raw_response': ai_result['content'],
                'model': ai_result['model'],
                'finish_reason': ai_result['finish_reason'],
            })

        save_trip_plan_for_user(
            request,
            planner_input=planner_input,
            plan_payload={},
            raw_response=ai_result['content'],
            model_name=ai_result['model'],
            finish_reason=ai_result['finish_reason'],
        )

        return JsonResponse({
            'success': True,
            'structured': False,
            'raw_response': ai_result['content'],
            'model': ai_result['model'],
            'finish_reason': ai_result['finish_reason'],
        })

    except ValueError:
        return JsonResponse({'error': 'Please enter valid trip details.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except OpenRouterRequestError as exc:
        return JsonResponse({'error': str(exc)}, status=exc.status)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def rush_calculator_api(request):
    """Estimate expected crowd rush for a selected place and visit slot."""
    try:
        data = json.loads(request.body)
        place_id = int(data.get('place_id', 0))
        visit_day = data.get('visit_day', 'Saturday').strip() or 'Saturday'
        time_slot = data.get('time_slot', 'evening').strip() or 'evening'
        special_event = data.get('special_event', 'normal').strip() or 'normal'

        place = TouristPlace.objects.filter(place_id=place_id).first()
        if not place:
            return JsonResponse({'error': 'Please select a valid place.'}, status=400)

        result = calculate_rush_estimate(place, visit_day, time_slot, special_event)
        return JsonResponse({
            'success': True,
            'result': result,
        })

    except ValueError:
        return JsonResponse({'error': 'Please enter valid rush calculator details.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@require_http_methods(["GET"])
def timetable_lookup_api(request):
    """Return temple timetable or full details by selected guide."""
    ensure_temple_guides_loaded()
    guide_id = request.GET.get('guide_id')
    query = request.GET.get('q', '').strip()
    mode = request.GET.get('mode', 'details').strip() or 'details'

    guide = None
    if guide_id:
        guide = TempleGuide.objects.filter(id=guide_id).first()
    elif query:
        guide = TempleGuide.objects.filter(name__icontains=query).order_by('name').first()
        if not guide:
            normalized_query = normalize_lookup_key(query)
            for candidate in TempleGuide.objects.all():
                if normalize_lookup_key(candidate.name) == normalized_query:
                    guide = candidate
                    break
                if any(normalize_lookup_key(alias) == normalized_query for alias in candidate.aliases or []):
                    guide = candidate
                    break

    if not guide:
        return JsonResponse({'error': 'Temple details not found.'}, status=404)

    return JsonResponse({
        'success': True,
        'guide': serialize_temple_guide(guide, mode=mode),
    })


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """AI Chatbot API endpoint using OpenRouter."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        image_url = data.get('image_url', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        primary_model, _ = get_openrouter_models()

        if is_identity_query(user_message):
            identity_response = build_identity_response(primary_model)
            save_chat_history_for_user(
                request,
                user_message=user_message,
                assistant_response=identity_response,
                model_name='identity_override',
                finish_reason='identity_override',
            )
            return JsonResponse({
                'success': True,
                'response': identity_response,
                'weather': "",
                'model': primary_model,
                'finish_reason': 'identity_override',
            })

        system_prompt = (
            "You are Mathura Darshan Assistant, a warm and polished spiritual travel guide "
            "for Mathura and Vrindavan, like a helpful local friend. "
            "Reply in the same language as the user, whether Hindi, Hinglish, or English. "
            "Sound natural, respectful, practical, and conversational, not robotic. "
            "Start with the direct answer, then add a few useful details, tips, or next steps. "
            "Use short sections or clean bullet points only when they genuinely improve clarity. "
            "Answer about Mathura temples (Krishna Janmabhoomi, Dwarkadhish, Vishram Ghat), "
            "ghats, food, hotels, festivals (Holi, Janmashtami), routes, local customs, and culture. "
            "If someone asks for timings, prices, transport, weather, or crowd updates, mention that "
            "these can change and local confirmation is wise. "
            "Avoid speculative, controversial, or legal claims unless the user explicitly asks about them. "
            "Never mention creator, owner, developer, or branding details in normal travel answers. "
            "Only if the user explicitly asks about your developer, creator, owner, or model, do not mention any technical model name. "
            "In that case, clearly say: 'Mathura Tourism by Sheetal. I am made by Sheetal Kashyap from Sanskriti University.' "
            "Keep most answers concise but genuinely helpful."
        )

        if image_url:
            prompted_content = [
                {
                    'type': 'text',
                    'text': f'{system_prompt}\n\nUser question: {user_message}',
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': image_url,
                    },
                },
            ]
        else:
            prompted_content = f'{system_prompt}\n\nUser question: {user_message}'

        ai_result = send_openrouter_chat(
            messages=[
                {'role': 'user', 'content': prompted_content},
            ],
            temperature=0.7,
            max_tokens=int(os.getenv('OPENROUTER_MAX_TOKENS', '900')),
        )

        ai_response = ai_result['content']
        finish_reason = ai_result['finish_reason']

        if finish_reason == 'length':
            ai_response = (
                f'{ai_response}\n\n'
                'Response yahin cut ho gaya. Please ask "continue" and I will carry on from here.'
            )

        weather_info = ""
        if any(word in user_message.lower() for word in ['weather', 'rain', 'temperature', 'cold', 'hot']):
            weather_info = get_weather()

        save_chat_history_for_user(
            request,
            user_message=user_message,
            assistant_response=ai_response,
            weather_info=weather_info,
            model_name=ai_result['model'],
            finish_reason=finish_reason,
        )

        return JsonResponse({
            'success': True,
            'response': ai_response,
            'weather': weather_info,
            'model': ai_result['model'],
            'finish_reason': finish_reason,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except OpenRouterRequestError as exc:
        return JsonResponse({'error': str(exc)}, status=exc.status)
    except requests.RequestException as exc:
        return JsonResponse({'error': f'Request failed: {str(exc)}'}, status=500)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


def get_weather():
    """Fetch weather information for Mathura."""
    try:
        weather_api_key = os.getenv('WEATHER_API_KEY', '')
        if not weather_api_key:
            return ""

        response = requests.get(
            'https://api.openweathermap.org/data/2.5/weather',
            params={
                'q': 'Mathura',
                'appid': weather_api_key,
                'units': 'metric',
            },
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"Current weather in Mathura: {temp}°C, {description}"
        return ""

    except Exception as e:
        return ""
