from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from .models import Booking, Hotel

@shared_task
def send_booking_confirmation_email(booking_id):
    """
    Sends a confirmation email to the user upon successful booking.
    """
    try:
        # Retrieve the booking instance from the database using its ID
        booking = Booking.objects.get(id=booking_id)
        user = booking.user
        hotel = booking.hotel
        
        subject = f"Booking Confirmation for {hotel.name}"
        message = f"""
        Hi {user.first_name or user.username},

        Thank you for your booking at {hotel.name}!

        Your booking details are as follows:
        - Check-in: {booking.check_in_date}
        - Check-out: {booking.check_out_date}
        - Guests: {booking.num_guests}

        We look forward to welcoming you.

        Best regards,
        The ALX Travel Team
        """
        
        # Send the email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or 'noreply@alxtravel.com',
            [user.email],
            fail_silently=False,
        )
        return f"Confirmation email sent to {user.email} for booking {booking_id}"
    
    except Booking.DoesNotExist:
        # Handle the case where the booking might have been deleted before the task ran
        return f"Booking with id {booking_id} not found."
    except Exception as e:
        print(f"An error occurred while sending email for booking {booking_id}: {e}")
        return f"Failed to send email for booking {booking_id}."
