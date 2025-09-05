from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from PIL import Image
import os
from django.conf import settings

class BaseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=11)
    gender = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    class Meta:
        abstract = True

class Passenger(BaseUser):
    def __str__(self):
        return f"Passenger: {self.fname}"

class Driver(BaseUser):
    """
    Driver model for storing driver information.
    Note: vehicle_papers are stored in MEDIA_ROOT/vehicle_papers/ directory.
    Make sure MEDIA_ROOT is properly configured in settings.py
    """
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    vehicle_papers = models.FileField(
        upload_to='vehicle_papers/',
        null=True,
        help_text="Upload vehicle registration and insurance documents. Files will be stored in MEDIA_ROOT/vehicle_papers/"
    )
    
    def __str__(self):
        return f"Driver: {self.fname}"

class Mycar(models.Model):
    """
    Mycar model for storing car information.
    Note: car images are stored in MEDIA_ROOT/cars/ directory.
    Make sure MEDIA_ROOT is properly configured in settings.py
    """
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    car_num = models.CharField(max_length=10)  # Remove unique=True from here
    car_name = models.CharField(max_length=30)
    company = models.CharField(max_length=30)
    car_type = models.CharField(max_length=30)
    from_place = models.CharField(max_length=30)
    to_place = models.CharField(max_length=30)
    date=models.DateField()
    time=models.TimeField(null=True, blank=True)  # Modified to allow null values
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()
    price_per_seat = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Price per Seat (₹)"
    )
    car_img = models.ImageField(
        upload_to='cars/',
        null=True, 
        blank=True,
        help_text="Upload car images. Files will be stored in MEDIA_ROOT/cars/"
    )

    class Meta:
        # Make car_num unique per driver
        unique_together = ['driver', 'car_num']
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'

    def __str__(self):
        return f"{self.car_name} ({self.car_num})"

    @property
    def imageURL(self):
        try:
            if self.car_img:
                return self.car_img.url
            return ''
        except Exception as e:
            return ''

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        if self.price_per_seat is None or self.price_per_seat <= 0:
            raise ValidationError({'price_per_seat': 'Please enter a valid price per seat (greater than 0).'})
            
        if self.total_seats <= 0:
            raise ValidationError({'total_seats': 'Total seats must be greater than 0.'})
            
        if self.available_seats > self.total_seats:
            raise ValidationError({'available_seats': 'Available seats cannot exceed total seats.'})
            
        if self.date and self.date < timezone.now().date():
            raise ValidationError({'date': 'Date cannot be in the past.'})

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            super().save(*args, **kwargs)
            if self.car_img:  # Only process image if one exists
                img = Image.open(self.car_img.path)
                if img.height > 1500 or img.width > 1500:
                    output_size = (1500, 1500)
                    img.thumbnail(output_size)
                    img.save(self.car_img.path)
        except ValidationError:
            self.price_per_seat = max(0.01, self.price_per_seat)
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the image file when deleting the car
        if self.car_img:
            if os.path.isfile(self.car_img.path):
                os.remove(self.car_img.path)
        super().delete(*args, **kwargs)

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='bookings')
    car = models.ForeignKey(Mycar, on_delete=models.SET_NULL, null=True, blank=True)  # Allow null for car
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    contact = models.CharField(max_length=15)
    email = models.EmailField()
    pickup = models.DateField()
    dropoff = models.DateField()
    pick_add = models.CharField(max_length=200)
    drop_add = models.CharField(max_length=200)
    seats_booked = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    feedback = models.TextField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.status}"

    def clean(self):
        if self.pickup > self.dropoff:
            raise ValidationError({'pickup': 'Pickup date cannot be after dropoff date.'})
        
        if self.pickup < timezone.now().date():
            raise ValidationError({'pickup': 'Pickup date cannot be in the past.'})
            
        if self.seats_booked <= 0:
            raise ValidationError({'seats_booked': 'Number of seats must be greater than 0.'})
            
        if self.car and self.seats_booked > self.car.available_seats:
            raise ValidationError({'seats_booked': 'Cannot book more seats than available.'})

    def save(self, *args, **kwargs):
        if not self.total_price and self.car and self.seats_booked:
            self.total_price = self.car.price_per_seat * self.seats_booked
        super().save(*args, **kwargs)

class ContactUs(models.Model):
    name=models.CharField(max_length=80)
    email=models.EmailField(max_length=80, unique=True, blank=False)
    phone=models.CharField(max_length=11, blank=False)  # Remove null=False since blank=False covers it
    msg=models.CharField(max_length=200)

    def __str__(self):
        return self.name