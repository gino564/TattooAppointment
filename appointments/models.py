from django.db import models
from django.contrib.auth.models import User


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    client_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    tattoo_design = models.TextField()
    reference_image = models.ImageField(upload_to='appointments/designs/', blank=True, null=True)
    selected_style = models.ForeignKey('TattooStyle', on_delete=models.SET_NULL, null=True, blank=True)
    preferred_artist = models.ForeignKey('Artist', on_delete=models.SET_NULL, null=True, blank=True)
    body_placement = models.CharField(max_length=100, blank=True)
    appointment_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Appointment approval status'
    )
    rejection_reason = models.TextField(blank=True, help_text='Reason for rejection (if rejected)')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.client_name} - {self.appointment_date}"
    
    class Meta:
        ordering = ['-appointment_date']


class TattooStyle(models.Model):
    """Different tattoo styles offered by the studio"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='styles/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Alternative to image upload")
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']


class Artist(models.Model):
    """Tattoo artists in the studio"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('resident', 'Resident Artist'),
        ('guest', 'Guest Artist'),
        ('apprentice', 'Apprentice'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    bio = models.TextField(blank=True)
    # Use both image field and URL (flexible approach)
    image = models.ImageField(upload_to='artists/profile_pics/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Alternative to image upload")
    portfolio_url = models.URLField(blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"
    
    def get_image_url(self):
        """Return image URL - either from uploaded file or external URL"""
        if self.image:
            return self.image.url
            return self.image_url if self.image_url else ''
    
    class Meta:
        ordering = ['order', 'name']


class Studio(models.Model):
    """Studio locations"""
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    image = models.ImageField(upload_to='studios/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    def get_image_url(self):
        """Return image URL - either from uploaded file or external URL"""
        if self.image:
            return self.image.url
        return self.image_url
    
    class Meta:
        ordering = ['order', 'name']


class Review(models.Model):
    """Client testimonials"""
    client_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    review_text = models.TextField()
    date = models.DateField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.client_name} - {self.rating}★"
    
    class Meta:
        ordering = ['-date']


class Enquiry(models.Model):
    """Tattoo enquiries from landing page"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    preferred_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_contacted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.email}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Enquiries"