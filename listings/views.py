from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
import uuid
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import redirect
from .models import Payment, Booking
# listings/views.py
from rest_framework import viewsets, permissions, status
from .tasks import send_booking_confirmation_email


# Assuming a booking_id is passed to initiate payment
class InitiatePaymentAPIView(APIView):
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        tx_ref = str(uuid.uuid4()) # Generate a unique transaction reference
        
        # Prepare the payload for Chapa API
        payload = {
            "amount": str(booking.total_price),
            "currency": "ETB",
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "tx_ref": tx_ref,
            "callback_url": f"http://127.0.0.1:8000/api/payments/verify/{tx_ref}/", # Redirect to our verify endpoint
            "return_url": f"http://127.0.0.1:8000/booking/{booking.id}/success" # URL for user after payment
        }
        
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(settings.CHAPA_INITIATE_URL, json=payload, headers=headers)
            response.raise_for_status() # Raise an error for bad status codes
            
            chapa_response_data = response.json()
            if chapa_response_data['status'] == 'success':
                # Create a new payment record with a 'pending' status
                Payment.objects.create(
                    booking=booking,
                    chapa_reference=tx_ref,
                    amount=booking.total_price,
                    status='pending'
                )
                
                # Redirect the user to the payment URL provided by Chapa
                return redirect(chapa_response_data['data']['checkout_url'])
            else:
                return Response({"error": chapa_response_data.get('message', 'Payment initiation failed')}, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Chapa API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPaymentAPIView(APIView):
    def get(self, request, tx_ref):
        try:
            payment = Payment.objects.get(chapa_reference=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }
        
        try:
            response = requests.get(f"{settings.CHAPA_VERIFY_URL}{tx_ref}", headers=headers)
            response.raise_for_status()
            
            chapa_verification_data = response.json()
            if chapa_verification_data['status'] == 'success':
                # Check if the transaction is verified and update the payment status
                if chapa_verification_data['data']['status'] == 'success':
                    payment.status = 'completed'
                    payment.save()
                    # Trigger the background task for email confirmation
                    send_booking_confirmation_email.delay(payment.booking.id)
                    return Response({"message": "Payment verified and booking confirmed."}, status=status.HTTP_200_OK)
                else:
                    payment.status = 'failed'
                    payment.save()
                    return Response({"message": "Payment failed."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": chapa_verification_data.get('message', 'Verification failed')}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Chapa API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Save the booking and get the instance
        booking = serializer.save(user=self.request.user)
        
        # Trigger the Celery task to send a confirmation email asynchronously
        # The .delay() method is a shortcut for a task to be run by the Celery worker
        send_booking_confirmation_email.delay(booking.id)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)