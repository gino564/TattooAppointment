from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponse
import csv
from .models import Appointment, TattooStyle, Artist, Studio, Review, Enquiry

# ============================================================
# APPOINTMENT ADMIN (YOUR EXISTING CODE - KEEP IT!)
# ============================================================

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Enhanced Admin interface for managing tattoo appointments with approval system
    """
    
    # ============================================================
    # LIST DISPLAY CONFIGURATION
    # ============================================================
    list_display = [
        'client_name',
        'email', 
        'phone',
        'tattoo_design_short',
        'appointment_date',
        'created_at',
        'status_badge',
        'appointment_status_badge'
    ]
    
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['client_name', 'email', 'phone', 'tattoo_design']
    date_hierarchy = 'appointment_date'
    list_per_page = 25
    
    # Fields to display in the edit form
    fields = [
        'client_name',
        'email',
        'phone',
        'tattoo_design',
        'appointment_date',
        'status',
        'created_at'
    ]
    
    readonly_fields = ['created_at']
    
    # ============================================================
    # CUSTOM ACTIONS
    # ============================================================
    actions = [
        'approve_appointments',
        'reject_appointments', 
        'mark_as_pending',
        'export_to_csv',
        'mark_as_contacted'
    ]
    
    def approve_appointments(self, request, queryset):
        """Bulk action to approve selected appointments"""
        updated = queryset.update(status='approved')
        self.message_user(
            request,
            f'✅ Successfully approved {updated} appointment(s)!'
        )
    approve_appointments.short_description = '✅ Approve selected appointments'
    
    def reject_appointments(self, request, queryset):
        """Bulk action to reject selected appointments"""
        updated = queryset.update(status='rejected')
        self.message_user(
            request,
            f'❌ Successfully rejected {updated} appointment(s)!'
        )
    reject_appointments.short_description = '❌ Reject selected appointments'
    
    def mark_as_pending(self, request, queryset):
        """Bulk action to mark appointments as pending"""
        updated = queryset.update(status='pending')
        self.message_user(
            request,
            f'⏳ Marked {updated} appointment(s) as pending review.'
        )
    mark_as_pending.short_description = '⏳ Mark as pending review'
    
    def export_to_csv(self, request, queryset):
        """Export selected appointments to CSV file"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="appointments_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Client Name', 'Email', 'Phone', 'Tattoo Design',
            'Appointment Date', 'Status', 'Created At'
        ])
        
        for appointment in queryset:
            writer.writerow([
                appointment.client_name,
                appointment.email,
                appointment.phone,
                appointment.tattoo_design,
                appointment.appointment_date.strftime('%Y-%m-%d %H:%M'),
                appointment.get_status_display(),
                appointment.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_to_csv.short_description = '📥 Export selected to CSV'
    
    def mark_as_contacted(self, request, queryset):
        """Mark appointments as contacted"""
        count = queryset.count()
        self.message_user(
            request,
            f'📞 Marked {count} appointment(s) as contacted.'
        )
    mark_as_contacted.short_description = '📞 Mark as contacted'
    
    # ============================================================
    # CUSTOM DISPLAY METHODS
    # ============================================================
    
    def tattoo_design_short(self, obj):
        """Display truncated tattoo design in list view"""
        max_length = 30
        design = obj.tattoo_design
        if len(design) > max_length:
            return f"{design[:max_length]}..."
        return design
    tattoo_design_short.short_description = '🎨 Tattoo Design'
    tattoo_design_short.admin_order_field = 'tattoo_design'
    
    def status_badge(self, obj):
        """Display colored status badge"""
        status_colors = {
            'pending': '#FFA500',  # Orange
            'approved': '#28A745',  # Green
            'rejected': '#DC3545'   # Red
        }
        status_labels = {
            'pending': '⏳ PENDING',
            'approved': '✅ APPROVED',
            'rejected': '❌ REJECTED'
        }
        
        color = status_colors.get(obj.status, '#6C757D')
        label = status_labels.get(obj.status, obj.status.upper())
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            label
        )
    status_badge.short_description = '📊 Approval Status'
    
    def appointment_status_badge(self, obj):
        """Display if appointment is upcoming or completed"""
        now = timezone.now()
        if obj.appointment_date > now:
            return format_html(
                '<span style="color: #28A745; font-weight: bold;">✓ UPCOMING</span>'
            )
        return format_html(
            '<span style="color: #6C757D; font-weight: bold;">✓ COMPLETED</span>'
        )
    appointment_status_badge.short_description = '📅 Time Status'
    
    # ============================================================
    # CUSTOM MESSAGES
    # ============================================================
    
    def save_model(self, request, obj, form, change):
        """Custom save with notification message"""
        super().save_model(request, obj, form, change)
        if change:
            self.message_user(
                request,
                f'✓ Appointment for {obj.client_name} updated successfully!'
            )
        else:
            self.message_user(
                request,
                f'✓ New appointment for {obj.client_name} created successfully!'
            )
    
    def delete_model(self, request, obj):
        """Custom delete with notification"""
        client_name = obj.client_name
        super().delete_model(request, obj)
        self.message_user(
            request,
            f'✓ Appointment for {client_name} deleted successfully.'
        )


# ============================================================
# NEW MODELS ADMIN (ADD THESE - FOR LANDING PAGE)
# ============================================================

@admin.register(TattooStyle)
class TattooStyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'order', 'is_active', 'instagram']
    list_filter = ['role', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'bio']
    ordering = ['order', 'name']


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'phone', 'is_active', 'order']
    list_filter = ['country', 'is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['name', 'city', 'country', 'address']
    ordering = ['order', 'name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'rating', 'is_approved', 'is_featured', 'date']
    list_filter = ['rating', 'is_approved', 'is_featured', 'date']
    list_editable = ['is_approved', 'is_featured']
    search_fields = ['client_name', 'review_text']
    ordering = ['-date']
    date_hierarchy = 'date'


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'preferred_date', 'is_contacted', 'created_at']
    list_filter = ['is_contacted', 'created_at', 'preferred_date']
    list_editable = ['is_contacted']
    search_fields = ['name', 'email', 'phone', 'message']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


# ============================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================

admin.site.site_header = "💀 J'ink Studio - Admin Panel"
admin.site.site_title = "J'ink Admin"
admin.site.index_title = "Manage Tattoo Appointments & Content"