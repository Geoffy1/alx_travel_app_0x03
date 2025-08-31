from rest_framework import serializers
from .models import Listing, Booking

class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Listing model.
    """
    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'price_per_night',
            'country',
            'city',
            'image_url',
            'created_at'
        ]

class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    """
    # To display listing and user details instead of just their IDs
    listing = ListingSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'listing',
            'check_in_date',
            'check_out_date',
            'guests',
            'created_at'
        ]
