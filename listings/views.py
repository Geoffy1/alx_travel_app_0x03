from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides CRUD operations for Listing objects.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides CRUD operations for Booking objects.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer