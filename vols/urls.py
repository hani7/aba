from django.urls import path
# force reload
from . import views

app_name = 'vols'

urlpatterns = [
    # ── Home ──────────────────────────────────────────────────────────────
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('faq/', views.faq, name='faq'),
    path('destinations/', views.destinations_list_view, name='destinations_list'),
    path('activities/', views.activities_view, name='activities_list'),

    # ── Flights (Duffel) ──────────────────────────────────────────────────
    path('api/places/', views.api_places, name='api_places'),
    path('rechercher/', views.search_results, name='search_results'),
    path('offre/<str:offer_id>/', views.passenger_details, name='passenger_details'),
    path('confirmer/', views.confirm_booking, name='confirm_booking'),

    path('mes-reservations/', views.my_bookings, name='my_bookings'),

    # ── Hotels (Agoda) ────────────────────────────────────────────────────
    path('hotels/', views.hotel_search, name='hotel_search'),
    path('hotels/resultats/', views.hotel_results, name='hotel_results'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('hotels/reserver/', views.hotel_book, name='hotel_book'),
    path('api/hotel-destinations/', views.api_hotel_destinations, name='api_hotel_destinations'),

    # ── Auth ──────────────────────────────────────────────────────────────
    path('inscription/', views.signup_view, name='signup'),
    path('verifier-email/', views.otp_verify_view, name='otp_verify'),
    path('connexion/', views.login_view, name='login'),
    path('deconnexion/', views.logout_view, name='logout'),
    
    # ── Admin Dashboard API ───────────────────────────────────────────────
    # Stripe Checkout URLs
    path('stripe/pay/<int:booking_id>/', views.stripe_pay, name='stripe_pay'),
    path('stripe/success/', views.stripe_success, name='stripe_success'),
    path('stripe/cancel/', views.stripe_cancel, name='stripe_cancel'),

    # Payment Choice page
    path('payment/<int:booking_id>/', views.payment_choice, name='payment_choice'),

    # Admin Dashboard API
    path('api/admin/stats/', views.api_admin_stats, name='api_admin_stats'),
    path('api/admin/bookings/', views.api_admin_bookings, name='api_admin_bookings'),
    path('api/admin/clients/', views.api_admin_clients, name='api_admin_clients'),
    path('api/admin/bookings/<int:booking_id>/cancel/', views.api_admin_cancel_booking, name='api_admin_cancel_booking'),
    path('api/admin/bookings/<int:booking_id>/issue/', views.api_admin_issue_booking, name='api_admin_issue_booking'),
    path('api/admin/ticket/<int:booking_id>/pdf/', views.generate_ticket_pdf, name='generate_ticket_pdf'),
    
    # ── React Dashboard (Vanilla/Babel) ──────────────────────────────────
    path('fa/', views.react_dashboard_view, name='react_admin_panel'),
]
