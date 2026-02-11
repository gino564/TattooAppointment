from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Appointment, TattooStyle, Artist, Review, PortfolioImage

class RegisterForm(UserCreationForm):
    """Custom registration form with additional fields"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        })
        
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
    
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Custom login form with styled fields"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )



# ============================================
# BOOKING FORM FOR CLIENTS
# ============================================
class AppointmentBookingForm(forms.ModelForm):
    """Form for clients to book a tattoo session"""
    class Meta:
        model = Appointment
        fields = ['client_name', 'email', 'phone', 'tattoo_design',
                  'reference_image', 'selected_style', 'preferred_artist',
                  'body_placement', 'appointment_date']
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
            }),
            'tattoo_design': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your tattoo idea, size, style...',
                'rows': 4,
            }),
            'reference_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'selected_style': forms.Select(attrs={
                'class': 'form-control',
            }),
            'preferred_artist': forms.Select(attrs={
                'class': 'form-control',
            }),
            'body_placement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Left forearm, Upper back...',
            }),
            'appointment_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_style'].queryset = TattooStyle.objects.filter(is_active=True)
        self.fields['selected_style'].empty_label = 'Choose a style (optional)'
        self.fields['selected_style'].required = False
        self.fields['preferred_artist'].queryset = Artist.objects.filter(is_active=True)
        self.fields['preferred_artist'].empty_label = 'Choose an artist (optional)'
        self.fields['preferred_artist'].required = False


# ============================================
# REJECTION FORM FOR ADMINS
# ============================================
class RejectionForm(forms.Form):
    """Form for admin to provide rejection reason"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Reason for rejection...',
            'rows': 3,
        }),
        required=True,
    )


# ============================================
# REVIEW FORM FOR CLIENTS
# ============================================
class ReviewForm(forms.ModelForm):
    """Form for clients to leave a review"""
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-control',
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience...',
                'rows': 4,
            }),
        }


# ============================================
# ARTIST MANAGEMENT FORMS (ADMIN ONLY)
# ============================================
class ArtistForm(forms.ModelForm):
    """Form for admin to add/edit an artist"""
    class Meta:
        model = Artist
        fields = ['name', 'role', 'bio', 'image', 'instagram', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Artist Name',
            }),
            'role': forms.Select(attrs={
                'class': 'form-control',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Artist bio / description...',
                'rows': 4,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@handle (without @)',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


# ============================================
# STYLE MANAGEMENT FORMS (ADMIN ONLY)
# ============================================
class TattooStyleForm(forms.ModelForm):
    """Form for admin to add/edit a tattoo style"""
    class Meta:
        model = TattooStyle
        fields = ['name', 'description', 'image', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Style Name (e.g. Portrait Realism)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of this style...',
                'rows': 3,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }