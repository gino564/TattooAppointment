from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, EnquiryForm
from django.views.generic import ListView
from .models import Appointment, TattooStyle, Artist, Studio, Review, Enquiry



# ============================================
# PUBLIC LANDING PAGE (NO LOGIN REQUIRED)
# ============================================

def landing_page(request):
    """Public landing page - Homepage"""
    styles = TattooStyle.objects.filter(is_active=True)[:4]
    artists = Artist.objects.filter(is_active=True)[:8]
    studios = Studio.objects.filter(is_active=True)[:2]
    reviews = Review.objects.filter(is_approved=True, is_featured=True)[:4]
    
    context = {
        'styles': styles,
        'artists': artists,
        'studios': studios,
        'reviews': reviews,
    }
    return render(request, 'appointments/landing.html', context)


def enquiry_submit(request):
    """Handle tattoo enquiry form submission"""
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            # Check if user is authenticated
            if not request.user.is_authenticated:
                # Store form data in session for later submission
                request.session['pending_enquiry'] = {
                    'name': form.cleaned_data.get('name'),
                    'email': form.cleaned_data.get('email'),
                    'phone': form.cleaned_data.get('phone'),
                    'message': form.cleaned_data.get('message'),
                    'preferred_date': form.cleaned_data.get('preferred_date').isoformat() if form.cleaned_data.get('preferred_date') else None,
                }
                messages.info(request, '🔑 Please login or register to submit your tattoo enquiry.')
                return redirect('appointments:login')

            # User is authenticated, save the enquiry
            form.save()
            messages.success(request, '✨ Thank you for your enquiry! We\'ll get back to you within 24 hours. 💀')
            return redirect('appointments:landing')
        else:
            messages.error(request, 'Please correct the errors in the form.')
            return redirect('appointments:landing')
    return redirect('appointments:landing')


# ============================================
# AUTHENTICATION VIEWS (Login appears first)
# ============================================

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('appointments:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Check if there's a pending enquiry in session
                if 'pending_enquiry' in request.session:
                    from datetime import date
                    enquiry_data = request.session['pending_enquiry']

                    # Convert date string back to date object if present
                    if enquiry_data.get('preferred_date'):
                        enquiry_data['preferred_date'] = date.fromisoformat(enquiry_data['preferred_date'])

                    # Create and save the enquiry
                    Enquiry.objects.create(**enquiry_data)

                    # Clear the session data
                    del request.session['pending_enquiry']

                    messages.success(request, f'Welcome back, {username}! Your tattoo enquiry has been submitted successfully. 💀')
                    return redirect('appointments:landing')
                else:
                    messages.success(request, f'Welcome back, {username}! 💀')

                # Redirect to 'next' parameter or default to index page
                next_url = request.GET.get('next', 'appointments:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'appointments/login.html', {'form': form})

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('appointments:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # Auto-login the user after registration
            login(request, user)

            # Check if there's a pending enquiry in session
            if 'pending_enquiry' in request.session:
                from datetime import date
                enquiry_data = request.session['pending_enquiry']

                # Convert date string back to date object if present
                if enquiry_data.get('preferred_date'):
                    enquiry_data['preferred_date'] = date.fromisoformat(enquiry_data['preferred_date'])

                # Create and save the enquiry
                Enquiry.objects.create(**enquiry_data)

                # Clear the session data
                del request.session['pending_enquiry']

                messages.success(request, f'Welcome, {username}! Your account has been created and your tattoo enquiry has been submitted successfully. 💀')
                return redirect('appointments:landing')
            else:
                messages.success(request, f'Account created for {username}! Welcome to J\'INK Studio. 💀')
                return redirect('appointments:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()

    return render(request, 'appointments/register.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('appointments:login')

# ============================================
# PROTECTED VIEWS (Require login)
# ============================================

@login_required(login_url='appointments:login')
def index(request):
    return render(request, 'appointments/index.html')

@login_required(login_url='appointments:login')
def appointment_list_fbv(request):
    """Function-Based View (FBV) - Protected"""
    appointments = Appointment.objects.all()
    context = {
        'appointments': appointments,
        'view_type': 'Function-Based View (FBV)'
    }
    return render(request, 'appointments/appointment_list.html', context)

class AppointmentListCBV(LoginRequiredMixin, ListView):
    """Class-Based View (CBV) - Protected"""
    login_url = 'appointments:login'
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'Class-Based View (CBV)'
        return context

# ============================================
# EDIT AND DELETE VIEWS
# ============================================

@login_required(login_url='appointments:login')
def appointment_edit(request, pk):
    """Edit an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment.client_name = request.POST.get('client_name')
        appointment.email = request.POST.get('email')
        appointment.phone = request.POST.get('phone')
        appointment.tattoo_design = request.POST.get('tattoo_design')
        appointment.appointment_date = request.POST.get('appointment_date')
        appointment.save()
        
        messages.success(request, f'Appointment for {appointment.client_name} updated successfully! 💀')
        return redirect('appointments:list-fbv')
    
    return render(request, 'appointments/edit.html', {'appointment': appointment})

@login_required(login_url='appointments:login')
def appointment_delete(request, pk):
    """Delete an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        client_name = appointment.client_name
        appointment.delete()
        messages.success(request, f'Appointment for {client_name} has been deleted. 💀')
        return redirect('appointments:list-fbv')
    
    return render(request, 'appointments/delete_confirm.html', {'appointment': appointment})