""" from celery import shared_task
from django.core.mail import send_mail
from .models import Booking

@shared_task
def send_booking_confirmation_email(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        subject = f"Booking Confirmation for {booking.listing.title}"
        message = f"Hello {booking.user.username},\n\nYour booking for {booking.listing.title} has been successfully confirmed.\nTotal Price: {booking.total_price}\n\nThank you!"
        from_email = 'noreply@yourdomain.com'
        recipient_list = [booking.user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        print(f"Confirmation email sent for booking {booking_id}")

    except Booking.DoesNotExist:
        print(f"Booking with ID {booking_id} not found.")
    except Exception as e:
        print(f"Failed to send email for booking {booking_id}: {e}") """

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_booking_confirmation_email(booking_id):
    """
    Sends a booking confirmation email asynchronously using Celery.
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'Booking Confirmation for your stay at {booking.listing.title}'
        message = (f'Hello {booking.user.username},\n\n'
                   f'Thank you for your booking! Your reservation for {booking.listing.title} '
                   f'from {booking.check_in_date} to {booking.check_out_date} '
                   f'has been confirmed.\n\n'
                   f'Booking ID: {booking.id}\n'
                   f'Total Cost: ${booking.total_cost}\n\n'
                   'We look forward to hosting you!\n\n'
                   'The alx_travel_app team.')
        
        from_email = settings.DEFAULT_FROM_EMAIL or 'noreply@your_travel_app.com'
        recipient_list = [booking.user.email]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        logger.info(f"Booking confirmation email sent successfully for booking {booking_id}")
        return f"Email sent for booking {booking_id}"
    
    except Booking.DoesNotExist:
        logger.error(f"Booking with ID {booking_id} not found. Cannot send email.")
        return "Booking not found"
    except Exception as e:
        logger.error(f"Failed to send email for booking {booking_id}: {e}")
        raise