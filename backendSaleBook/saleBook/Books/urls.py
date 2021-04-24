from django.urls import path
from .views import *
# from Books.views import DownloadPDF
urlpatterns = [
    # path('download/', DownloadPDF, name='download_pdf'),
    path('pay/', start_payment, name="payment"),
    path('payment/success/', handle_payment_success, name="payment_success")
]