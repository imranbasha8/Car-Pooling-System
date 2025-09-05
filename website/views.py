from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import transaction
import os
from .models import Passenger, Driver, Mycar, Booking

def home(request):
    return render(request, "home.html")

def Contactus(request):
    if request.method == "POST":
        # ...handle contact form submission...
        pass
    return render(request, "contact.html")

# Passenger Views
def PassengerLogin(request):
    if request.method == "POST":
        usern = request.POST['usern']
        password = request.POST['password']
        user = authenticate(username=usern, password=password)
        try:
            passenger = Passenger.objects.get(user=user)
            login(request, user)
            return redirect('passenger_dashboard')
        except:
            messages.error(request, "Invalid credentials!")
    return render(request, "passenger/login.html")

def PassengerRegister(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=request.POST['usern'],
                    email=request.POST['email'],
                    password=request.POST['password']
                )
                passenger = Passenger.objects.create(
                    user=user,
                    fname=request.POST['fname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    gender=request.POST['gender'],
                    address=request.POST['address'],
                    city=request.POST['city'],
                    state=request.POST['state']
                )
                messages.success(request, "Registration successful! Please login.")
                return redirect('passenger_login')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, "passenger/register.html")

@login_required(login_url='passenger_login')
def PassengerDashboard(request):
    try:
        passenger = request.user.passenger
    except Passenger.DoesNotExist:
        return redirect('home')
    available_rides = Mycar.objects.filter(available_seats__gt=0).order_by('date', 'time')
    return render(request, "passenger/dashboard.html", {'available_rides': available_rides})

@login_required(login_url='passenger_login')
def PassengerSearch(request):
    if request.method == "POST":
        from_place = request.POST.get('from_place')
        to_place = request.POST.get('to_place')
        date = request.POST.get('date')
        time=request.POST.get('time')
        
        # Search for available cars
        cars = Mycar.objects.filter(
            from_place__iexact=from_place,
            to_place__iexact=to_place,
            date__gte=date,
            time__gte=time
        )
        
        return render(request, "passenger/search_results.html", {'cars': cars})
    return render(request, "passenger/search.html")

@login_required(login_url='passenger_login')
def PassengerBookings(request):
    # Fix: 'name' to 'passenger'
    bookings = Booking.objects.filter(passenger=request.user.passenger)
    return render(request, "passenger/bookings.html", {'bookings': bookings})

# Driver Views
def DriverLogin(request):
    if request.method == "POST":
        usern = request.POST['usern']
        password = request.POST['password']
        user = authenticate(username=usern, password=password)
        try:
            driver = Driver.objects.get(user=user)
            login(request, user)
            return redirect('driver_dashboard')
        except:
            messages.error(request, "Invalid credentials!")
    return render(request, "driver/login.html")

def DriverRegister(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=request.POST['usern'],
                    email=request.POST['email'],
                    password=request.POST['password']
                )
                driver = Driver.objects.create(
                    user=user,
                    fname=request.POST['fname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    gender=request.POST['gender'],
                    address=request.POST['address'],
                    city=request.POST['city'],
                    state=request.POST['state'],
                    license_number=request.POST['license_number'],
                    license_expiry=request.POST['license_expiry'],
                    vehicle_papers=request.FILES.get('vehicle_papers')
                )
                messages.success(request, "Registration successful! ")
                return redirect('driver_login')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, "driver/register.html")

@login_required(login_url='driver_login')
def DriverDashboard(request):
    try:
        driver = request.user.driver
    except Driver.DoesNotExist:
        return redirect('home')
    
    cars = Mycar.objects.filter(driver=driver)
    pending_bookings = Booking.objects.filter(
        car__in=cars,
        status='pending'
    ).order_by('-id')
    
    active_bookings = Booking.objects.filter(
        car__in=cars,
        status='accepted'
    )
    
    context = {
        'cars': cars,
        'pending_bookings': pending_bookings,
        'active_bookings': active_bookings,
        'pending_count': pending_bookings.count()
    }
    return render(request, "driver/dashboard.html", context)

@login_required(login_url='driver_login')
def DriverBookings(request):
    cars = Mycar.objects.filter(driver=request.user.driver)
    bookings = Booking.objects.filter(car__in=cars).order_by('-id')
    # Group bookings by status
    pending_bookings = bookings.filter(status='pending')
    active_bookings = bookings.filter(status='accepted')
    completed_bookings = bookings.filter(status='completed')
    cancelled_bookings = bookings.filter(status='cancelled')
    
    context = {
        'pending_bookings': pending_bookings,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings
    }
    return render(request, "driver/bookings.html", {'context': context})

@login_required(login_url='driver_login')
def Addcar(request):
    try:
        driver = request.user.driver
    except Driver.DoesNotExist:
        return redirect('home')

    if request.method == "POST":
        try:
            total_seats = int(request.POST['total_seats'])
            available_seats = int(request.POST['available_seats'])
            
            if available_seats > total_seats:
                messages.error(request, "Available seats cannot be more than total seats")
                return render(request, "driver/addcar.html")
                
            if available_seats < 0:
                messages.error(request, "Available seats cannot be negative")
                return render(request, "driver/addcar.html")
                
            car = Mycar.objects.create(
                driver=driver,
                car_num=request.POST['car_num'],
                car_name=request.POST['car_name'],
                company=request.POST['company'],
                car_type=request.POST['car_type'],
                from_place=request.POST['from_place'],
                to_place=request.POST['to_place'],
                date=request.POST['date'],
                time=request.POST['time'],
                total_seats=total_seats,
                available_seats=available_seats,
                price_per_seat=request.POST['price_per_seat'],
                car_img=request.FILES.get('car_img')
            )
            messages.success(request, "Car added successfully!")
            return redirect('driver_dashboard')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, "driver/addcar.html")

# Booking Management
@login_required
def manage_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.car.driver != request.user.driver:
        messages.error(request, "You don't have permission to manage this booking")
        return redirect('driver_dashboard')
        
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'accept':
            # Update available seats when booking is accepted
            car = booking.car
            car.available_seats -= booking.seats_booked
            car.save()
            booking.status = 'accepted'
            messages.success(request, "Booking accepted successfully!")
        elif action == 'reject':
            booking.status = 'rejected'
            messages.success(request, "Booking rejected successfully!")
        elif action == 'complete':
            booking.status = 'completed'
            messages.success(request, "Booking marked as completed!")
        booking.save()
    
    return redirect('driver_bookings')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    # Fix: check against passenger instead of name.usern
    if booking.passenger.user == request.user:
        booking.status = 'cancelled'
        booking.save()
    return redirect('passenger_bookings')

def logout_user(request):
    """Handle user logout"""
    logout(request)
    return redirect('home')

@login_required(login_url='passenger_login')
def add_feedback(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Verify this is the passenger's booking
    if booking.passenger.user != request.user:  # Changed from booking.name.usern
        messages.error(request, "You cannot add feedback for this booking")
        return redirect('passenger_bookings')
        
    # Verify booking is completed
    if booking.status != 'completed':
        messages.error(request, "You can only add feedback for completed rides")
        return redirect('passenger_bookings')
        
    if request.method == "POST":
        booking.feedback = request.POST.get('feedback')
        booking.rating = request.POST.get('rating')
        booking.save()
        messages.success(request, "Thank you for your feedback!")
        
    return redirect('passenger_bookings')

def delete_car(request, car_id):
    try:
        car = get_object_or_404(Mycar, id=car_id, driver=request.user.driver)
        car.delete()
        messages.success(request, 'Car deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting car: {str(e)}')
    return redirect('driver_dashboard')

@login_required(login_url='passenger_login')
def book_ride(request, car_id):
    car = get_object_or_404(Mycar, id=car_id)
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                seats_required = int(request.POST['seats_required'])
                
                # Validate seats
                if seats_required > car.available_seats:
                    messages.error(request, f"Only {car.available_seats} seats available")
                    return redirect('book_ride', car_id=car_id)
                    
                if seats_required <= 0:
                    messages.error(request, "Please select at least 1 seat")
                    return redirect('book_ride', car_id=car_id)
                
                # Create booking
                booking = Booking.objects.create(
                    passenger=request.user.passenger,  # Fixed: changed from 'name' to 'passenger'
                    car=car,
                    contact=request.POST['contact'],
                    email=request.POST['email'],
                    pickup=car.date,
                    dropoff=car.date,
                    pick_add=request.POST['pick_add'],
                    drop_add=request.POST['drop_add'],
                    seats_booked=seats_required,
                    total_price=seats_required * car.price_per_seat,
                    status='pending'
                )
                
                messages.success(request, "Booking request sent successfully!")
                return redirect('passenger_bookings')
                
        except ValueError:
            messages.error(request, "Invalid number of seats")
        except Exception as e:
            messages.error(request, f"Booking failed: {str(e)}")
    
    return render(request, "passenger/book_ride.html", {'car': car})

@login_required(login_url='driver_login')
def update_car(request, car_id):
    car = get_object_or_404(Mycar, id=car_id, driver=request.user.driver)
    
    if request.method == "POST":
        try:
            car.car_name = request.POST['car_name']
            car.company = request.POST['company']
            car.car_type = request.POST['car_type']
            car.from_place = request.POST['from_place']
            car.to_place = request.POST['to_place']
            car.date = request.POST['date']
            car.time = request.POST['time']
            car.total_seats = request.POST['total_seats']
            car.available_seats = request.POST['available_seats']
            car.price_per_seat = request.POST['price_per_seat']
            
            if 'car_img' in request.FILES:
                # Delete old image if exists
                if car.car_img:
                    if os.path.isfile(car.car_img.path):
                        os.remove(car.car_img.path)
                car.car_img = request.FILES['car_img']
            
            car.save()
            messages.success(request, "Car updated successfully!")
            return redirect('driver_dashboard')
        except Exception as e:
            messages.error(request, f"Failed to update car: {str(e)}")
    
    return render(request, "driver/update_car.html", {'car': car})
