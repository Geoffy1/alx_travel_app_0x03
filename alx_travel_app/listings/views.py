from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import uuid
from .models import Booking, Payment
from .tasks import send_payment_confirmation_email
from .tasks import send_booking_confirmation_email

class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows listings to be viewed or edited.
    Provides GET, POST, PUT, PATCH, and DELETE methods.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    Provides GET, POST, PUT, PATCH, and DELETE methods.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def perform_create(self, serializer):
        """
        Save the booking and trigger a background task to send a confirmation email.
        """
        # Save the booking instance first
        booking = serializer.save(user=self.request.user)
        
        # Trigger the Celery task asynchronously using .delay()
        # We pass the booking ID because sending the whole object is not recommended.
        send_booking_confirmation_email.delay(booking.id)
    
    
CHAPA_API_URL = "https://api.chapa.co/v1/transaction/initialize"
CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify/"

class InitiatePaymentView(APIView):
    def post(self, request, *args, **kwargs):
        booking_id = request.data.get('booking_id')
        
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate a unique transaction reference
        tx_ref = f"tx-{booking.id}-{uuid.uuid4()}"
        
        # Details for Chapa API
        payload = {
            "amount": str(booking.amount),
            "currency": "KES",  # or your desired currency
            "email": booking.customer_email,
            "first_name": booking.customer_name.split()[0],
            "last_name": " ".join(booking.customer_name.split()[1:]),
            "tx_ref": tx_ref,
            "callback_url": f"http://127.0.0.1:8000/api/verify-payment/{tx_ref}/", #verification URL
            "return_url": "http://127.0.0.1:3000/payment-success/", # frontend success page
            "customization[title]": "Travel App Booking Payment",
            "customization[description]": f"Payment for booking ID {booking.id}"
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(CHAPA_API_URL, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                # Create a payment record in our database
                Payment.objects.create(
                    booking=booking,
                    amount=booking.amount,
                    tx_ref=tx_ref,
                    status=Payment.PaymentStatus.PENDING
                )
                # Return the checkout URL to the frontend
                return Response(response_data['data'], status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to initiate payment", "details": response_data.get('message')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except requests.exceptions.RequestException as e:
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VerifyPaymentView(APIView):
    def get(self, request, tx_ref, *args, **kwargs):
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }
        
        try:
            # Verify the transaction with Chapa
            response = requests.get(f"{CHAPA_VERIFY_URL}{tx_ref}", headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                payment_status = response_data.get('data', {}).get('status')
                
                try:
                    payment = Payment.objects.get(tx_ref=tx_ref)
                    
                    if payment_status == "success":
                        payment.status = Payment.PaymentStatus.COMPLETED
                        payment.save()
                        
                        # Trigger background task to send email
                        send_payment_confirmation_email.delay(payment.id)

                        return Response({"message": "Payment verified successfully."}, status=status.HTTP_200_OK)
                    else:
                        payment.status = Payment.PaymentStatus.FAILED
                        payment.save()
                        return Response({"message": "Payment failed or is still pending."}, status=status.HTTP_400_BAD_REQUEST)
                
                except Payment.DoesNotExist:
                    return Response({"error": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Failed to verify payment with Chapa."}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
