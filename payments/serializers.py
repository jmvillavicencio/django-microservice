from rest_framework import serializers
from .models import Payment, Refund


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating a PayPal order"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')
    description = serializers.CharField(required=False, allow_blank=True)


class CaptureOrderSerializer(serializers.Serializer):
    """Serializer for capturing a PayPal order"""
    order_id = serializers.CharField(max_length=50)


class RefundSerializer(serializers.Serializer):
    """Serializer for refunding a payment"""
    capture_id = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(max_length=3, default='USD')


class RefundModelSerializer(serializers.ModelSerializer):
    """Model serializer for Refund"""
    class Meta:
        model = Refund
        fields = ['id', 'paypal_refund_id', 'amount', 'status', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Model serializer for Payment"""
    refunds = RefundModelSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'paypal_order_id', 'amount', 'currency',
            'description', 'status', 'capture_id', 'created_at',
            'updated_at', 'refunds'
        ]
