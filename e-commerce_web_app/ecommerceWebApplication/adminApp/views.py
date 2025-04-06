from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.contrib import messages
from django.db.models import Max
from . import keys
from ecommerceApp.models import Product
from django.contrib.auth import logout

MERCHANT_KEY = keys.MERCHANT_KEY

def get_next_product_id(request):
    max_id = Product.objects.aggregate(max_id=Max('id'))['max_id'] or 0
    return JsonResponse({
        'next_id': max_id + 1,
        'pattern': 'NAME-CATEGORY-ID'  # For frontend reference
    })

@login_required
def admin_dashboard(request):
    if not (request.user.is_staff and request.user.is_active):
        return HttpResponseForbidden("Access Denied")
    
    if request.method == "GET":
        return render(request, "admin/dashboard.html")
    
    elif request.method == "POST":
        # Future logic for POST requests
        return HttpResponseBadRequest("Invalid request method")  # Placeholder for now
    
    return HttpResponseBadRequest("Invalid request method")


## Inventory
def stock_level(request):
    return render(request, "admin/inventory/stock_level.html")

def inventory_adjustment(request):
    return render(request, "admin/inventory/inventory_adjustment.html")

def inventory_history_log(request):
    return render(request, "admin/inventory/inventory_adjustment.html")

## Coupons/Discount
def coupons(request):
    return render(request, "admin/coupon_discount/coupons.html")

def discounts(request):
    return render(request, "admin/coupon_discount/discounts.html")

## Customers
@login_required
def customer_list_view(request):
    if not (request.user.is_staff and request.user.is_active):
        return HttpResponseForbidden("Access Denied")
    
    if request.method == "GET":
        return render(request, "admin/customers/customers_list.html")
    
    elif request.method == "POST":
        # Future logic for POST requests
        return HttpResponseBadRequest("Invalid request method")  # Placeholder for now
    
    return HttpResponseBadRequest("Invalid request method")


def staff_management(request):
    return render(request, "admin/customers/staff_management.html")


## Reports & Analysis
def reports_analysis(request):
    return render(request, "admin/reports/reports_analysis.html")

def system_log(request):
    return render(request, "admin/reports/system_logs.html")






def refund_request(request):
    return render(request, "admin/refund_request.html")


## Logout
def logout_view(request):
    logout(request)
    messages.info(request, "Logout Success")
    return redirect('/auth/login/')