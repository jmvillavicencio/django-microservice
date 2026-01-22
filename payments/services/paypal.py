import requests
from django.conf import settings


class PayPalClient:
    """PayPal REST API client"""
    
    SANDBOX_URL = 'https://api-m.sandbox.paypal.com'
    LIVE_URL = 'https://api-m.paypal.com'
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.base_url = self.SANDBOX_URL if settings.PAYPAL_MODE == 'sandbox' else self.LIVE_URL
        self._access_token = None
    
    def _get_access_token(self):
        """Obtain OAuth 2.0 access token from PayPal"""
        if self._access_token:
            return self._access_token
            
        url = f'{self.base_url}/v1/oauth2/token'
        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={'grant_type': 'client_credentials'}
        )
        response.raise_for_status()
        self._access_token = response.json()['access_token']
        return self._access_token
    
    def _get_headers(self):
        """Get headers with authorization"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._get_access_token()}'
        }
    
    def create_order(self, amount: str, currency: str = 'USD', description: str = None):
        """
        Create a PayPal order
        
        Args:
            amount: The amount to charge
            currency: Currency code (default: USD)
            description: Optional order description
        
        Returns:
            dict: PayPal order response
        """
        url = f'{self.base_url}/v2/checkout/orders'
        
        purchase_unit = {
            'amount': {
                'currency_code': currency,
                'value': amount
            }
        }
        if description:
            purchase_unit['description'] = description
        
        payload = {
            'intent': 'CAPTURE',
            'purchase_units': [purchase_unit]
        }
        
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def capture_order(self, order_id: str):
        """
        Capture payment for an approved order
        
        Args:
            order_id: The PayPal order ID
        
        Returns:
            dict: Capture response
        """
        url = f'{self.base_url}/v2/checkout/orders/{order_id}/capture'
        response = requests.post(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_order(self, order_id: str):
        """
        Get order details
        
        Args:
            order_id: The PayPal order ID
        
        Returns:
            dict: Order details
        """
        url = f'{self.base_url}/v2/checkout/orders/{order_id}'
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def refund_capture(self, capture_id: str, amount: str = None, currency: str = 'USD'):
        """
        Refund a captured payment
        
        Args:
            capture_id: The capture ID to refund
            amount: Optional amount to refund (full refund if not specified)
            currency: Currency code
        
        Returns:
            dict: Refund response
        """
        url = f'{self.base_url}/v2/payments/captures/{capture_id}/refund'
        
        payload = {}
        if amount:
            payload['amount'] = {
                'value': amount,
                'currency_code': currency
            }
        
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
