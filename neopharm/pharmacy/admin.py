from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User,
    LpacemakerDrugs,
    NcapDrugs,
    OncologyPharmacy,
    Cart,
    Form,
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'mobile', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'mobile', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'mobile', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'mobile', 'password1', 'password2'),
        }),
    )

class DrugAdminMixin:
    list_display = ('name', 'brand', 'unit', 'price', 'stock', 'exp_date', 'stock_status')
    list_filter = ('dosage_form', 'unit', 'brand')
    search_fields = ('name', 'brand')
    ordering = ('name',)
    
    def stock_status(self, obj):
        if obj.stock <= 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.stock < 10:
            return format_html('<span style="color: orange;">Low Stock</span>')
        return format_html('<span style="color: green;">In Stock</span>')
    
    stock_status.short_description = 'Stock Status'

@admin.register(LpacemakerDrugs)
class LpacemakerDrugsAdmin(DrugAdminMixin, admin.ModelAdmin):
    list_display = DrugAdminMixin.list_display + ('get_total_value',)
    
    def get_total_value(self, obj):
        total = float(obj.price * obj.stock)
        formatted_total = '{:,.2f}'.format(total)
        return format_html('₦{}', formatted_total)
    get_total_value.short_description = 'Total Value'

@admin.register(NcapDrugs)
class NcapDrugsAdmin(DrugAdminMixin, admin.ModelAdmin):
    list_display = DrugAdminMixin.list_display + ('get_total_value',)
    
    def get_total_value(self, obj):
        total = float(obj.price * obj.stock)
        formatted_total = '{:,.2f}'.format(total)
        return format_html('₦{}', formatted_total)
    get_total_value.short_description = 'Total Value'

@admin.register(OncologyPharmacy)
class OncologyPharmacyAdmin(DrugAdminMixin, admin.ModelAdmin):
    list_display = DrugAdminMixin.list_display + ('get_total_value',)
    
    def get_total_value(self, obj):
        total = float(obj.price * obj.stock)
        formatted_total = '{:,.2f}'.format(total)
        return format_html('₦{}', formatted_total)
    get_total_value.short_description = 'Total Value'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'user', 'get_drug_name', 'quantity', 'price', 'subtotal', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('cart_id', 'user__username', 'user__mobile')
    readonly_fields = ('cart_id', 'created_at')
    
    def get_drug_name(self, obj):
        if obj.lpacemaker_drug:
            return f"Lpacemaker: {obj.lpacemaker_drug.name}"
        elif obj.ncap_drug:
            return f"NCAP: {obj.ncap_drug.name}"
        elif obj.oncology_drug:
            return f"Oncology: {obj.oncology_drug.name}"
        return "No drug selected"
    get_drug_name.short_description = 'Drug'

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('form_id', 'buyer_name', 'total_amount', 'date', 'dispensed_by')
    list_filter = ('date', 'dispensed_by')
    search_fields = ('form_id', 'buyer_name', 'hospital_no', 'ncap_no')
    readonly_fields = ('form_id',)
    
    fieldsets = (
        ('Form Information', {
            'fields': ('form_id', 'buyer_name', 'hospital_no', 'ncap_no')
        }),
        ('Financial Details', {
            'fields': ('total_amount',)
        }),
        ('Additional Information', {
            'fields': ('date', 'dispensed_by')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('form_id', 'date')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # if creating new object
            obj.dispensed_by = request.user
        super().save_model(request, obj, form, change)

# Customize admin site header and title
admin.site.site_header = 'NEOPHARM Administration'
admin.site.site_title = 'NEOPHARM Admin Portal'
admin.site.index_title = 'Welcome to NEOPHARM Admin Portal'
# Register your models here.
