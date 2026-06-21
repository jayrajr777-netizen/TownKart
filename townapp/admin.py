from django.contrib import admin

from .models import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle











@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name','email' ,'contact_no' ,'password' , 'address',
                    'status' ,'role' ,'time_stamp' )

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('user','shop_name',"address",'email', 'contact_no', 'location')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 6


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_tag', 'price', 'qty', 'category', 'shop', 'sizes_available', 'product_type','description' ,'timestamp','status')
    inlines = [ProductImageInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'selected_size', 'quantity', 'status', 'cart_date' ,'total_amount' ,'orderid' )


def export_to_pdf(modeladmin, request, queryset):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'


    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []


    headers = ['User Name', 'Total Amount', 'Status', 'Order Date']


    data = [headers]
    for obj in queryset:

        date_str = obj.order_date.strftime("%d-%m-%Y") if obj.order_date else "N/A"
        data.append([obj.user.name, f"Rs. {obj.total_amount}", obj.status, date_str])


    t = Table(data)


    style = TableStyle([
        # Header Styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c4a491')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#ffffff')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fdfcfb')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2a2a2a')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),


        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2d1c3')),
    ])


    t.setStyle(style)
    elements.append(t)


    doc.build(elements)
    return response


export_to_pdf.short_description = "Export Selected Orders to PDF"
@admin.register(Order)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'order_date')
    actions = [export_to_pdf]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'amount', 'status' ,'user' ,'transaction_id')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'ratings', 'comment')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_id', 'status')


class SubProductImageInline(admin.TabularInline):
    model = SubProductImage
    extra = 2

@admin.register(SubProduct)
class SubProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_product', 'price', 'qty', 'status')
    inlines = [SubProductImageInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'timestamp')
    search_fields = ('name', 'email')
