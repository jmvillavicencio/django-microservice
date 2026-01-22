# PayPal Django Microservice

A microservice built with [Django](https://www.djangoproject.com/) and [Django REST Framework](https://www.django-rest-framework.org/) that provides a REST API for processing payments through PayPal.

## Features

- Full PayPal integration (create orders, capture payments, refunds)
- RESTful API with Django REST Framework
- Payment tracking with database models
- Support for both sandbox and live PayPal environments
- Health check endpoint

## Project Structure

```
django-microservice/
├── config/
│   ├── __init__.py
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Root URL configuration
│   └── wsgi.py                  # WSGI entry point
├── payments/
│   ├── migrations/
│   ├── services/
│   │   ├── __init__.py
│   │   └── paypal.py            # PayPal API client
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                # Payment & Refund models
│   ├── serializers.py           # DRF serializers
│   ├── urls.py                  # Payment routes
│   └── views.py                 # API views
├── manage.py
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10 or higher
- PayPal Developer account with API credentials

## Installation

```bash
# Navigate to the project
cd django-microservice

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

## Configuration

The service is configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PAYPAL_CLIENT_ID` | PayPal API client ID | *required* |
| `PAYPAL_CLIENT_SECRET` | PayPal API client secret | *required* |
| `PAYPAL_MODE` | PayPal environment (`sandbox` or `live`) | `sandbox` |
| `DJANGO_SECRET_KEY` | Django secret key | *insecure default* |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |

## Running the Service

```bash
# Set PayPal credentials
export PAYPAL_CLIENT_ID=your-client-id
export PAYPAL_CLIENT_SECRET=your-client-secret

# Run the development server
python manage.py runserver
```

The server will start on `http://localhost:8000`.

## API Endpoints

### Health Check

```
GET /api/payments/health/
```

**Response:**
```json
{
  "status": "ok"
}
```

### Create Order

Creates a new PayPal order for checkout.

```
POST /api/payments/orders/create/
```

**Request Body:**
```json
{
  "amount": "29.99",
  "currency": "USD",
  "description": "Product purchase"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | string | Yes | Payment amount |
| `currency` | string | No | Currency code (default: `USD`) |
| `description` | string | No | Order description |

**Response:**
```json
{
  "order_id": "5O190127TN364715T",
  "status": "CREATED",
  "links": [...],
  "payment_id": 1
}
```

### Capture Order

Captures payment after customer approval.

```
POST /api/payments/orders/capture/
```

**Request Body:**
```json
{
  "order_id": "5O190127TN364715T"
}
```

**Response:**
```json
{
  "order_id": "5O190127TN364715T",
  "status": "COMPLETED",
  "capture_id": "3C679366HH908993F"
}
```

### Get Order Details

Retrieves order details from PayPal.

```
GET /api/payments/orders/{order_id}/
```

### Refund Payment

Refunds a captured payment.

```
POST /api/payments/refund/
```

**Request Body:**
```json
{
  "capture_id": "3C679366HH908993F",
  "amount": "10.00",
  "currency": "USD"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `capture_id` | string | Yes | PayPal capture ID |
| `amount` | string | No | Partial refund amount (full refund if omitted) |
| `currency` | string | No | Currency code (default: `USD`) |

**Response:**
```json
{
  "refund_id": "1JU08902781691411",
  "status": "COMPLETED"
}
```

### List Payments

Returns all payment records.

```
GET /api/payments/
```

### Get Payment Details

Returns a specific payment record.

```
GET /api/payments/{id}/
```

## Example Usage

```bash
# Health check
curl http://localhost:8000/api/payments/health/

# Create an order
curl -X POST http://localhost:8000/api/payments/orders/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "19.99",
    "currency": "USD",
    "description": "Test purchase"
  }'

# Capture payment (after customer approval)
curl -X POST http://localhost:8000/api/payments/orders/capture/ \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "5O190127TN364715T"
  }'

# List all payments
curl http://localhost:8000/api/payments/
```

## Payment Flow

1. **Create Order**: Call `/api/payments/orders/create/` to create a PayPal order
2. **Customer Approval**: Redirect customer to PayPal using the `approve` link from the response
3. **Capture Payment**: After approval, call `/api/payments/orders/capture/` with the order ID
4. **Refund** (optional): Call `/api/payments/refund/` with the capture ID to process refunds

## Database Models

### Payment
- `paypal_order_id`: PayPal order identifier
- `amount`: Payment amount
- `currency`: Currency code
- `description`: Order description
- `status`: CREATED, APPROVED, CAPTURED, REFUNDED, or FAILED
- `capture_id`: PayPal capture identifier (after capture)

### Refund
- `payment`: Related payment record
- `paypal_refund_id`: PayPal refund identifier
- `amount`: Refund amount
- `status`: PENDING, COMPLETED, or FAILED

## License

MIT
