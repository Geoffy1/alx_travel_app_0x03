from django.core.management.base import BaseCommand
from listings.models import Listing
import decimal

class Command(BaseCommand):
    help = 'Seeds the database with sample listing data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to seed the database...'))

        # Clear existing data
        Listing.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing Listing data.'))

        # Sample data for listings
        sample_listings = [
            {
                "title": "Beachfront Villa in Diani",
                "description": "A stunning villa with a private pool and direct access to the beach.",
                "price_per_night": decimal.Decimal("250.00"),
                "country": "Kenya",
                "city": "Diani",
                "image_url": "https://images.unsplash.com/photo-1582610116397-edb3195b2344"
            },
            {
                "title": "Safari Lodge in Maasai Mara",
                "description": "Experience the wild in this luxurious lodge overlooking the Mara river.",
                "price_per_night": decimal.Decimal("400.50"),
                "country": "Kenya",
                "city": "Maasai Mara",
                "image_url": "https://images.unsplash.com/photo-1534533983685-c7b1e4a3a6a1"
            },
            {
                "title": "Cozy Apartment in Nairobi",
                "description": "A modern and stylish apartment in the heart of Westlands.",
                "price_per_night": decimal.Decimal("80.00"),
                "country": "Kenya",
                "city": "Nairobi",
                "image_url": "https://images.unsplash.com/photo-1596203993353-0c4837333604"
            },
            {
                "title": "Lakeside Cottage in Naivasha",
                "description": "A peaceful retreat by Lake Naivasha, perfect for bird watching.",
                "price_per_night": decimal.Decimal("120.75"),
                "country": "Kenya",
                "city": "Naivasha",
                "image_url": "https://images.unsplash.com/photo-1610399122363-2b91839e3b2e"
            },
            {
                "title": "Historic Swahili House in Lamu",
                "description": "Stay in a beautifully restored traditional house in Lamu Old Town.",
                "price_per_night": decimal.Decimal("150.00"),
                "country": "Kenya",
                "city": "Lamu",
                "image_url": "https://images.unsplash.com/photo-1603769116752-921869894c25"
            }
        ]

        # Create listing objects
        for data in sample_listings:
            Listing.objects.create(**data)

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(sample_listings)} listings.'))
