from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('orders/create/', views.CreateOrderView.as_view(), name='create-order'),
    path('orders/capture/', views.CaptureOrderView.as_view(), name='capture-order'),
    path('orders/<str:order_id>/', views.GetOrderView.as_view(), name='get-order'),
    path('refund/', views.RefundView.as_view(), name='refund'),
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<int:payment_id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
]
