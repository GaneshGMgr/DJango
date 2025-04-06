from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from .models import Contact
from .models import Order
from PayTm  import Checksum 


def index(request):
    # allProducts = []
    # catproducts = Products.objects.values('category', 'id')
    # cats = {item['category'] for item in catproducts}
    
    # for cat in cats:
    #     prod = Products.objects.filter(category=cat)
    #     n = len(prod)
    #     nSlides = n // 4 + ceil((n / 4) - (n // 4))
    #     allProducts.append([prod, range(1, nSlides + 1), nSlides])
    
    # params = {'allProds': allProducts}
    
    # return render(request, "index.html", params)
    return render(request, "index.html")



def about(request):
    return render(request,"about.html")


## Contact Us
@csrf_protect
def contact(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')

            if not all([name, email, subject, message]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'All fields are required.'
                })

            contactQuery = Contact(name=name, email=email, subject=subject, message=message)
            contactQuery.save()

            if contactQuery.id:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Your message has been sent successfully.'
                })

            return JsonResponse({
                'status': 'error',
                'message': 'Failed to send your message. Please try again later.'
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            })
    else:
        return render(request, 'contact.html')
    

# checkout view
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = float(request.POST.get('amt', 0))  # Ensure amount is a float
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        if not all([items_json, name, email, address1, city, state, zip_code, phone]):
            messages.warning(request, "All fields are required.")
            return redirect('/checkout')

        # Save the order
        order = Order(
            items_json=items_json, name=name, amount=amount,
            email=email, address1=address1, address2=address2,
            city=city, state=state, zip_code=zip_code, phone=phone
        )
        order.save()

        # Save order update
        # update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        # update.save()

        # Payment Integration
        oid = str(order.order_id) + "shopycart"
        param_dict = {
            'MID': keys.MID,
            'ORDER_ID': oid,
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',
        }

        checksum = Checksum(keys.MERCHANT_KEY)
        param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict)

        return render(request, 'paytm.html', {'param_dict': param_dict})

    return render(request, 'checkout.html')

@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {key: form[key] for key in form.keys()}

    checksum = form.get('CHECKSUMHASH')
    verify = Checksum(keys.MERCHANT_KEY).verify_checksum(response_dict, checksum)

    if verify:
        if response_dict['RESPCODE'] == '01':
            print('Order successful')

            order_id_raw = response_dict['ORDERID']
            amount_paid = response_dict['TXNAMOUNT']
            rid = order_id_raw.replace("shopycart", "")

            orders = Order.objects.filter(order_id=rid)
            for order in orders:
                order.oid = order_id_raw
                order.amountpaid = amount_paid
                order.paymentstatus = "PAID"
                order.save()

            print("Payment recorded successfully.")
        else:
            print(f"Order failed due to: {response_dict['RESPMSG']}")
    else:
        print("Checksum verification failed!")

    return render(request, 'paymentstatus.html', {'response': response_dict})








def checkoutview(request):
    return render(request, "paymentstatus.html")

# def profile(request):
    # if not request.user.is_authenticated:
    #     messages.warning(request, "Login & Try Again")
    #     return redirect('/authe/login')

    # currentuser = request.user.email
    # items = Orders.objects.filter(email=currentuser)

    # order_ids = [int(i.oid.replace("shopycart", "")) for i in items]
    # status = OrderUpdate.objects.filter(order_id__in=order_ids)
    # status_list = [
    #     {
    #         "order_id": s.order_id, 
    #         "msg": s.update_desc,
    #         "delivered_status": s.delivered_status,
    #         "timestamp": s.timestamp,
    #     }
    #     for s in status
    # ]
    # context = {"items": items, "status": status_list}
    # return render(request, "profile.html", context)
    return render(request, "profile.html")