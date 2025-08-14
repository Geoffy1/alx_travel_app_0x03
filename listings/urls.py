from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payments/initiate/<int:booking_id>/', InitiatePaymentAPIView.as_view(), name='initiate-payment'),
    path('payments/verify/<str:tx_ref>/', VerifyPaymentAPIView.as_view(), name='verify-payment'),
]