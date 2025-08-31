from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, InitiatePaymentView, VerifyPaymentView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
     path('api/initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('api/verify-payment/<str:tx_ref>/', VerifyPaymentView.as_view(), name='verify-payment'),
]
