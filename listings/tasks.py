from celery import shared_task
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
        print(f"Failed to send email for booking {booking_id}: {e}")