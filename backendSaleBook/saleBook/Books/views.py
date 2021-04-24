from django.shortcuts import render
import json

import environ
import razorpay
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


from django.core.files import File
from django.http import HttpResponse
from rest_framework.decorators import api_view
from saleBook.settings import BASE_DIR, MEDIA_ROOT
env = environ.Env()
environ.Env.read_env()

@api_view(['GET'])
def start_payment(request):
    
    print(request.data)
    amount = 500
    name = 'Finance Book'

    
    client = razorpay.Client(auth=(env('PUBLIC_KEY'), env('SECRET_KEY')))

 
    payment = client.order.create({"amount": int(amount) * 100, 
                                   "currency": "INR", 
                                   "payment_capture": "1"})

    order = Order.objects.create(order_product=name, 
                                 order_amount=amount, 
                                 order_payment_id=payment['id'])

    serializer = OrderSerializer(order)


    data = {
        "payment": payment,
        "order": serializer.data
    }
    return Response(data)




@api_view(['POST'])
def handle_payment_success(request):
  
    res = json.loads(request.data["response"])

   

    ord_id = ""
    raz_pay_id = ""
    raz_signature = ""


    for key in res.keys():
        if key == 'razorpay_order_id':
            ord_id = res[key]
        elif key == 'razorpay_payment_id':
            raz_pay_id = res[key]
        elif key == 'razorpay_signature':
            raz_signature = res[key]

    order = Order.objects.get(order_payment_id=ord_id)

    data = {
        'razorpay_order_id': ord_id,
        'razorpay_payment_id': raz_pay_id,
        'razorpay_signature': raz_signature
    }

    client = razorpay.Client(auth=(env('PUBLIC_KEY'), env('SECRET_KEY')))

    check = client.utility.verify_payment_signature(data)

    if check is not None:
        print("Redirect to error url or error page")
        return Response({'error': 'Something went wrong'})

    order.isPaid = True
    order.save()
    

    path_to_file = MEDIA_ROOT + '/Gateways Comparision.pdf'
    f = open(path_to_file, 'rb')
    pdfFile = File(f)
    response = HttpResponse(pdfFile.read(),content_type='application/pdf')
    response['Content-Disposition'] =  'attachment; filename="Gateways Comparision.pdf"'
    return response
    




# @api_view(['GET'])
# def DownloadPDF(self):
#     path_to_file = MEDIA_ROOT + '/Gateways Comparision.pdf'
#     f = open(path_to_file, 'rb')
#     pdfFile = File(f)
#     response = HttpResponse(pdfFile.read(),content_type='application/pdf')
#     response['Content-Disposition'] =  'attachment; filename="Gateways Comparision.pdf"'
#     return response