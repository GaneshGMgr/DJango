from django.urls import path
from adminApp import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name="admin-dashboard"),
    path('api/get-next-product-id/', views.get_next_product_id, name='next_product_id'),
    path('logout/', views.logout_view, name="logout"),
    path('refund/', views.refund_request, name="refund_request"),

    # customers
    path('customer-list/', views.customer_list_view, name="customer-list"),
    path('staff-management/', views.staff_management, name="staff-management"),

    # inventory
    path("stock-level/", views.stock_level, name="stocklevel"),
    path("inventory-adjustment/", views.inventory_adjustment, name="inventoryadjustment"),
    path("inventory-history-log/", views.inventory_history_log, name="inventoryhistorylog"),

    # coupon/discount
    path("coupon/", views.coupons, name="coupons"),
    path("discount/", views.discounts, name="discounts"),

    # Reports
    path("reports/analysis/", views.reports_analysis, name="reportanalysis"),
    path("system/logs/", views.system_log, name="systemlogs"),

]