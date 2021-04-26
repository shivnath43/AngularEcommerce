from django.shortcuts import render
import json

import environ
import razorpay
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer

from django.http import FileResponse
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
    print(json.dumps(request.data['params']['razorpay_order_id']))

    # res1 = json.dumps(request.data)

    # res = json.loads(res1)
    # # print(res1.params['razorpay_order_id'])
   

    ord_id = request.data['params']['razorpay_order_id']
    raz_pay_id = request.data['params']['razorpay_payment_id']
    raz_signature =  request.data['params']['razorpay_signature']
    

    # for key in res.keys():
    #     if key == 'razorpay_order_id':
    #         ord_id = res[key]
    #         # print(ord_id)
    #     elif key == 'razorpay_payment_id':
    #         raz_pay_id = res[key]
    #         # print(raz_pay_id)
    #     elif key == 'razorpay_signature':
    #         raz_signature = res[key]
    #         # print(raz_signature)

    
    try:
       order = Order.objects.get(order_payment_id=ord_id)
    except Order.DoesNotExist:
       order = None
    data = {
        'razorpay_order_id': ord_id,
        'razorpay_payment_id': raz_pay_id,
        'razorpay_signature': raz_signature
    }
    print(data)
    client = razorpay.Client(auth=(env('PUBLIC_KEY'), env('SECRET_KEY')))

    check = client.utility.verify_payment_signature(data)

    if check is not None:
        print("Redirect to error url or error page")
        return Response({'error': 'Something went wrong'})

    order.isPaid = True

    order.save()
    # filename='Gateways Comparision.pdf'
    # response=DownloadPDF(filename)
    path_to_file = MEDIA_ROOT + '/Gateways Comparision.pdf'
    f = open(path_to_file, 'rb')
    response = FileResponse(f)
    # pdfFile = File(f)
    # response = HttpResponse(pdfFile.read(),content_type='application/pdf')
    # response['Content-Disposition'] =  'attachment; filename="Gateways Comparision.pdf"'
    print(response)
   
    return response
    





# def DownloadPDF(self):
#     path_to_file = MEDIA_ROOT + '/Gateways Comparision.pdf'
#     f = open(path_to_file, 'rb')
#     pdfFile = File(f)
#     response = HttpResponse(pdfFile.read(),content_type='application/pdf')
#     response['Content-Disposition'] =  'attachment; filename="Gateways Comparision.pdf"'
#     return response