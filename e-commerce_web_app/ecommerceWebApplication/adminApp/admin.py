## adminApp/admin.py
from django.utils.text import slugify
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Max
from django.utils import timezone
from authApp.models import User, UserProfile, Address
from ecommerceApp.models import Product, Category, Order, OrderItem, Payment, ProductImage, ProductVariant, Cart, CartItem, Wishlist, Refund, Contact

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'current_price', 'is_active')
    readonly_fields = ('sku_preview',)
    actions = ['regenerate_skus']
    
    def sku_preview(self, obj):
        if not obj.pk:  # For new unsaved objects
            max_id = Product.objects.aggregate(max_id=Max('id'))['max_id'] or 0
            next_id = max_id + 1
            name_part = slugify(obj.name[:5]).upper().replace('-', '')
            cat_part = slugify(obj.category.name[:3]).upper().replace('-', '')
            preview = f"{name_part}-{cat_part}-{next_id}"
            return format_html('<span class="text-success">Auto-SKU: <strong>{}</strong></span>', preview)
        return obj.sku or "Not generated yet"
    
    def regenerate_skus(self, request, queryset):
        for product in queryset.filter(sku__isnull=True):
            product.save()
        self.message_user(request, f"SKUs regenerated for {queryset.count()} products")
    regenerate_skus.short_description = "Regenerate missing SKUs"

# Register remaining models
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    prepopulated_fields = {'slug': ['name']}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'tracking_number')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    raw_id_fields = ('order', 'product')

# Auth models
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender')
    raw_id_fields = ('user',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'is_default')
    list_filter = ('is_default', 'address_type')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'requested_at')
    list_filter = ('status',)
    actions = ['approve_refunds', 'reject_refunds']
    readonly_fields = ('order', 'reason', 'requested_at')

    def approve_refunds(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"Approved {queryset.count()} refund(s)")
    approve_refunds.short_description = "Approve selected refunds"

    def reject_refunds(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"Rejected {queryset.count()} refund(s)")
    reject_refunds.short_description = "Reject selected refunds"

    def save_model(self, request, obj, form, change):
        if obj.status == 'processed':
            obj.processed_at = timezone.now()
        super().save_model(request, obj, form, change)


# Other admin registrations with basic configurations
admin.site.register(Payment)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Contact)