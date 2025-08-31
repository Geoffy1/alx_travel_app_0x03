# ALX Travel App - Milestone 3: API Development

This project extends the base travel application with a RESTful API for managing listings and bookings.

## API Endpoints

The API is accessible under the `/api/` path and provides the following endpoints:

### Listings

-   **GET `/api/listings/`**: Retrieve a list of all listings.
-   **POST `/api/listings/`**: Create a new listing.
-   **GET `/api/listings/{id}/`**: Retrieve details for a specific listing.
-   **PUT/PATCH `/api/listings/{id}/`**: Update an existing listing.
-   **DELETE `/api/listings/{id}/`**: Delete a listing.

### Bookings

-   **GET `/api/bookings/`**: Retrieve a list of all bookings.
-   **POST `/api/bookings/`**: Create a new booking.
-   **GET `/api/bookings/{id}/`**: Retrieve details for a specific booking.
-   **PUT/PATCH `/api/bookings/{id}/`**: Update an existing booking.
-   **DELETE `/api/bookings/{id}/`**: Delete a booking.

### API Documentation

Full API documentation (Swagger UI) is available at `/swagger/`.# alx_travel_app_0x01

# alx_travel_app_0x03

This project is a travel booking application built with Django and Django REST Framework. This version introduces background task processing using Celery and RabbitMQ for sending email notifications.

## Prerequisites

- Python 3.x
- Django & Django REST Framework
- Celery
- RabbitMQ

### RabbitMQ Installation

You need to have RabbitMQ installed and running on your system.
For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server# alx_travel_app_0x03
