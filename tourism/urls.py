from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('explore/', views.explore, name='explore'),
    path('plan-trip/', views.plan_trip_page, name='plan_trip'),
    path('rush-calculator/', views.rush_calculator_page, name='rush_calculator'),
    path('timetable-finder/', views.timetable_finder_page, name='timetable_finder'),
    path('place/<int:place_id>/', views.place_detail, name='place_detail'),
    path('navigation/', views.navigation, name='navigation'),
    path('chatbot/', views.chatbot_page, name='chatbot'),
    path('services/', views.services, name='services'),
    path('favourites/', views.favourites, name='favourites'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('chatbot/api/', views.chatbot_api, name='chatbot_api'),
    path('plan-trip/api/', views.plan_trip_api, name='plan_trip_api'),
    path('rush-calculator/api/', views.rush_calculator_api, name='rush_calculator_api'),
    path('timetable-finder/api/', views.timetable_lookup_api, name='timetable_lookup_api'),
]
