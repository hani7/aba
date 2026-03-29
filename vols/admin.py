from django.contrib import admin
from .models import Booking, Passenger


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'origin', 'destination', 'departure_date', 'airline', 'status', 'total_amount', 'currency', 'created_at']
    list_filter = ['status', 'cabin_class', 'currency']
    search_fields = ['booking_reference', 'duffel_order_id', 'origin', 'destination']
    inlines = [PassengerInline]
    readonly_fields = ['duffel_order_id', 'booking_reference', 'created_at', 'updated_at']
    actions = ['cancel_bookings']

    @admin.action(description="Annuler les vols sélectionnés chez Duffel")
    def cancel_bookings(self, request, queryset):
        success_count = 0
        error_count = 0
        
        # We need duffel_service
        from .services import duffel_service
        
        for booking in queryset:
            if booking.status == 'cancelled':
                continue
                
            try:
                result = duffel_service.cancel_order(booking.duffel_order_id)
                # If everything went well or it was already cancelled
                booking.status = 'cancelled'
                booking.save()
                success_count += 1
            except Exception as e:
                self.message_user(request, f"Erreur pour {booking.booking_reference} : {str(e)}", level='error')
                error_count += 1
                
        if success_count > 0:
            self.message_user(request, f"{success_count} réservation(s) ont été annulées avec succès chez Duffel.", level='success')


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'born_on', 'booking']
    search_fields = ['first_name', 'last_name', 'email']
