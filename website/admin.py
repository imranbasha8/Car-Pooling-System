from django.contrib import admin
from website.models import Passenger, Driver, Booking, ContactUs, Mycar

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['fname', 'email', 'mobile']
    search_fields = ['fname', 'email', 'mobile']

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['fname', 'email', 'mobile', 'license_number', 'license_expiry']
    search_fields = ['fname', 'email', 'mobile', 'license_number']

@admin.register(Mycar)
class MycarAdmin(admin.ModelAdmin):
    list_display = ['car_name', 'car_num', 'driver', 'from_place', 'to_place', 'available_seats']
    search_fields = ['car_name', 'car_num', 'from_place', 'to_place']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'passenger', 'car', 'status', 'pickup', 'seats_booked']
    list_filter = ['status']
    search_fields = ['passenger__fname', 'car__car_num']

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name', 'email']