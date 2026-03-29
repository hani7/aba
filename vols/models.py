from django.db import models
from django.contrib.auth.models import User
import random, string
from django.utils import timezone
from datetime import timedelta


class EmailOTP(models.Model):
    """One-time password sent to user email for account verification."""
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_otp')
    code    = models.CharField(max_length=6)
    created = models.DateTimeField(auto_now_add=True)

    def generate(self):
        self.code = ''.join(random.choices(string.digits, k=6))
        self.save()
        return self.code

    def is_valid(self, entered_code):
        """Code valid for 10 minutes."""
        age = timezone.now() - self.created
        return self.code == entered_code and age < timedelta(minutes=10)

    def __str__(self):
        return f'OTP for {self.user.username}: {self.code}'


class Booking(models.Model):
    """Represents a confirmed flight booking via Duffel."""
    duffel_order_id = models.CharField(max_length=100, unique=True)
    booking_reference = models.CharField(max_length=20)
    
    # Flight info
    origin = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    departure_date = models.DateField()
    airline = models.CharField(max_length=100, blank=True)
    flight_number = models.CharField(max_length=20, blank=True)
    cabin_class = models.CharField(max_length=30, blank=True)
    
    # Financial
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    markup_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=5, default='EUR')
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('paid', 'Payé'),
        ('cancelled', 'Annulé'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.booking_reference} — {self.origin} → {self.destination}'


class Passenger(models.Model):
    """Passenger linked to a booking."""
    GENDER_CHOICES = [('m', 'Masculin'), ('f', 'Féminin')]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    duffel_passenger_id = models.CharField(max_length=100, blank=True)
    
    title = models.CharField(max_length=10, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    born_on = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class HotelBooking(models.Model):
    """Tracks a hotel booking made via Agoda affiliate."""

    # Hotel info
    hotel_id    = models.IntegerField()
    hotel_name  = models.CharField(max_length=200)
    city_name   = models.CharField(max_length=100)
    check_in    = models.DateField()
    check_out   = models.DateField()
    nights      = models.PositiveIntegerField(default=1)
    adults      = models.PositiveIntegerField(default=2)
    rooms       = models.PositiveIntegerField(default=1)

    # Financial — the key profit tracking fields
    cost_price     = models.DecimalField(max_digits=10, decimal_places=2, help_text='Agoda real price')
    markup_pct     = models.DecimalField(max_digits=5,  decimal_places=2, default=10)
    markup_amount  = models.DecimalField(max_digits=10, decimal_places=2, help_text='Your profit')
    customer_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price charged to customer')
    currency       = models.CharField(max_length=5, default='USD')

    # Guest info
    guest_name  = models.CharField(max_length=200)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=30, blank=True)

    # Booking status
    STATUS_CHOICES = [
        ('pending',   'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
    ]
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    agoda_ref  = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.hotel_name} — {self.guest_name} ({self.check_in}→{self.check_out})'

    @property
    def profit(self):
        return self.markup_amount
