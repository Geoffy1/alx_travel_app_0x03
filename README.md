# alx_travel_app_0x03

This project enhances the ALX Travel App by introducing asynchronous background tasks using Celery and RabbitMQ to handle email notifications for new bookings.

## Milestone 5: Background Email Notifications

This feature ensures that the user receives a fast response when creating a booking, as the time-consuming process of sending an email is offloaded to a background worker.

### Setup and Installation

1.  **Clone the repository and install dependencies:**
    ```bash
    git clone <your-repo-url>
    cd alx_travel_app_0x03
    pip install -r requirements.txt
    ```

2.  **Run RabbitMQ using Docker:**
    Make sure you have Docker installed and running.
    ```bash
    docker run -d -p 5672:5672 -p 15672:15672 --name my-rabbitmq rabbitmq:3-management
    ```

### How to Run the Application

You need to run three services in separate terminal windows:

1.  **Start the RabbitMQ Container** (if not already running):
    ```bash
    docker start my-rabbitmq
    ```

2.  **Start the Celery Worker:**
    This worker listens for and executes background tasks.
    ```bash
    celery -A alx_travel_app worker -l info
    ```

3.  **Start the Django Development Server:**
    ```bash
    python manage.py runserver
    ```

Now, you can make API requests to `http://127.0.0.1:8000/`. When a new booking is created, a confirmation email will be sent in the background. For development, the email content is printed to the Django server's console.
