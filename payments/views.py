import logging
from decimal import Decimal

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from requests.exceptions import HTTPError

from .models import Payment, Refund
from .serializers import (
    CreateOrderSerializer,
    CaptureOrderSerializer,
    RefundSerializer,
    PaymentSerializer,
)
from .services import PayPalClient


logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Health check endpoint"""
    
    def get(self, request):
        return Response({'status': 'ok'})


class CreateOrderView(APIView):
    """Create a PayPal order"""
    
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        client = PayPalClient()
        
        try:
            result = client.create_order(
                amount=str(data['amount']),
                currency=data.get('currency', 'USD'),
                description=data.get('description', '')
            )
            
            # Save payment record
            payment = Payment.objects.create(
                paypal_order_id=result['id'],
                amount=data['amount'],
                currency=data.get('currency', 'USD'),
                description=data.get('description', ''),
                status=Payment.Status.CREATED
            )
            
            return Response({
                'order_id': result['id'],
                'status': result['status'],
                'links': result.get('links', []),
                'payment_id': payment.id
            }, status=status.HTTP_201_CREATED)
            
        except HTTPError as e:
            logger.error(f'PayPal API error: {e}')
            return Response(
                {'error': 'Failed to create PayPal order'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class CaptureOrderView(APIView):
    """Capture payment for an approved order"""
    
    def post(self, request):
        serializer = CaptureOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        client = PayPalClient()
        
        try:
            result = client.capture_order(order_id)
            
            # Update payment record
            capture_id = ''
            if result.get('purchase_units'):
                captures = result['purchase_units'][0].get('payments', {}).get('captures', [])
                if captures:
                    capture_id = captures[0].get('id', '')
            
            Payment.objects.filter(paypal_order_id=order_id).update(
                status=Payment.Status.CAPTURED,
                capture_id=capture_id
            )
            
            return Response({
                'order_id': result['id'],
                'status': result['status'],
                'capture_id': capture_id
            })
            
        except HTTPError as e:
            logger.error(f'PayPal API error: {e}')
            Payment.objects.filter(paypal_order_id=order_id).update(
                status=Payment.Status.FAILED
            )
            return Response(
                {'error': 'Failed to capture payment'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class GetOrderView(APIView):
    """Get order details from PayPal"""
    
    def get(self, request, order_id):
        client = PayPalClient()
        
        try:
            result = client.get_order(order_id)
            return Response(result)
        except HTTPError as e:
            logger.error(f'PayPal API error: {e}')
            return Response(
                {'error': 'Failed to get order details'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class RefundView(APIView):
    """Refund a captured payment"""
    
    def post(self, request):
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        client = PayPalClient()
        
        try:
            amount = str(data['amount']) if data.get('amount') else None
            result = client.refund_capture(
                capture_id=data['capture_id'],
                amount=amount,
                currency=data.get('currency', 'USD')
            )
            
            # Update payment and create refund record
            payment = Payment.objects.filter(capture_id=data['capture_id']).first()
            if payment:
                refund_amount = Decimal(amount) if amount else payment.amount
                Refund.objects.create(
                    payment=payment,
                    paypal_refund_id=result['id'],
                    amount=refund_amount,
                    status=Refund.Status.COMPLETED
                )
                payment.status = Payment.Status.REFUNDED
                payment.save()
            
            return Response({
                'refund_id': result['id'],
                'status': result['status']
            })
            
        except HTTPError as e:
            logger.error(f'PayPal API error: {e}')
            return Response(
                {'error': 'Failed to process refund'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class PaymentListView(APIView):
    """List all payments"""
    
    def get(self, request):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentDetailView(APIView):
    """Get payment details"""
    
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
