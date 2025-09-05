from django.urls import path
from website import views

urlpatterns = [
    # Common URLs
    path('', views.home, name="home"),
    path('contact/', views.Contactus, name="contact"),
    
    # Passenger URLs
    path('passenger/login/', views.PassengerLogin, name="passenger_login"),
    path('passenger/register/', views.PassengerRegister, name="passenger_register"),
    path('passenger/dashboard/', views.PassengerDashboard, name="passenger_dashboard"),
    path('passenger/search/', views.PassengerSearch, name="passenger_search"),
    path('passenger/bookings/', views.PassengerBookings, name="passenger_bookings"),
    path('passenger/book-ride/<int:car_id>/', views.book_ride, name='book_ride'),  # Add this line
    
    # Driver URLs
    path('driver/login/', views.DriverLogin, name="driver_login"),
    path('driver/register/', views.DriverRegister, name="driver_register"),
    path('driver/dashboard/', views.DriverDashboard, name="driver_dashboard"),
    path('driver/car/add/', views.Addcar, name="addcar"),
    path('driver/bookings/', views.DriverBookings, name="driver_bookings"),
    path('driver/update-car/<int:car_id>/', views.update_car, name='update_car'),
    
    # Booking Management
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/manage/', views.manage_booking, name='manage_booking'),
    path('booking/<int:booking_id>/feedback/', views.add_feedback, name='add_feedback'),

    # Logout URL
    path('logout/', views.logout_user, name='logout'),  # Add this line
    path('delete-car/<int:car_id>/', views.delete_car, name='delete_car'),
]   