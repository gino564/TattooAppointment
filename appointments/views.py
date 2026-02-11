from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, AppointmentBookingForm, RejectionForm, ReviewForm, ArtistForm
from django.views.generic import ListView
from .models import Appointment, TattooStyle, Artist, Studio, Review, PortfolioImage



# ============================================
# PUBLIC LANDING PAGE (NO LOGIN REQUIRED)
# ============================================

def landing_page(request):
    """Public landing page - Homepage"""
    styles = TattooStyle.objects.filter(is_active=True)[:4]
    artists = Artist.objects.filter(is_active=True)[:4]
    studios = Studio.objects.filter(is_active=True)[:2]
    reviews = Review.objects.filter(is_approved=True)[:8]

    context = {
        'styles': styles,
        'artists': artists,
        'studios': studios,
        'reviews': reviews,
    }
    return render(request, 'appointments/landing.html', context)



# ============================================
# AUTHENTICATION VIEWS
# ============================================

def login_view(request):
    """User login view - redirects admin to admin dashboard, client to client dashboard"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('appointments:admin_dashboard')
        return redirect('appointments:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')

                # Role-based redirect
                if user.is_staff:
                    return redirect('appointments:admin_dashboard')
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
            messages.success(request, f'Account created for {username}! Welcome to J\'INK Studio.')
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
# CLIENT VIEWS (Require login)
# ============================================

@login_required(login_url='appointments:login')
def index(request):
    """Client dashboard - shows user's appointments"""
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments/index.html', {'appointments': appointments})

@login_required(login_url='appointments:login')
def book_session(request):
    """Client booking page with gallery picker and custom upload"""
    styles = TattooStyle.objects.filter(is_active=True)
    artists = Artist.objects.filter(is_active=True)

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, request.FILES)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.status = 'pending'

            # Handle selected style from gallery click (hidden input)
            style_id = request.POST.get('gallery_style_id')
            if style_id:
                try:
                    appointment.selected_style = TattooStyle.objects.get(pk=style_id)
                except TattooStyle.DoesNotExist:
                    pass

            appointment.save()
            messages.success(request, 'Your session has been booked! We\'ll review it shortly.')
            return redirect('appointments:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill client info from user profile
        form = AppointmentBookingForm(initial={
            'client_name': f'{request.user.first_name} {request.user.last_name}'.strip() or request.user.username,
            'email': request.user.email,
        })

    return render(request, 'appointments/book_session.html', {
        'form': form,
        'styles': styles,
        'artists': artists,
    })

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

        messages.success(request, f'Appointment for {appointment.client_name} updated successfully!')
        return redirect('appointments:index')

    return render(request, 'appointments/edit.html', {'appointment': appointment})

@login_required(login_url='appointments:login')
def appointment_delete(request, pk):
    """Delete an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        client_name = appointment.client_name
        appointment.delete()
        messages.success(request, f'Appointment for {client_name} has been deleted.')
        return redirect('appointments:index')

    return render(request, 'appointments/delete_confirm.html', {'appointment': appointment})


# ============================================
# ADMIN VIEWS (Require staff)
# ============================================

def staff_required(view_func):
    """Decorator that requires user to be staff"""
    @login_required(login_url='appointments:login')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('appointments:index')
        return view_func(request, *args, **kwargs)
    return wrapper

@staff_required
def admin_dashboard(request):
    """Admin dashboard - shows all appointments queue"""
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'all':
        appointments = Appointment.objects.all()
    else:
        appointments = Appointment.objects.filter(status=status_filter)

    counts = {
        'all': Appointment.objects.count(),
        'pending': Appointment.objects.filter(status='pending').count(),
        'approved': Appointment.objects.filter(status='approved').count(),
        'rejected': Appointment.objects.filter(status='rejected').count(),
    }

    return render(request, 'appointments/admin_dashboard.html', {
        'appointments': appointments,
        'counts': counts,
        'current_filter': status_filter,
    })

@staff_required
def admin_approve(request, pk):
    """Approve an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'approved'
    appointment.rejection_reason = ''
    appointment.save()
    messages.success(request, f'Appointment for {appointment.client_name} has been approved.')
    return redirect('appointments:admin_dashboard')

@staff_required
def admin_reject(request, pk):
    """Reject an appointment with reason"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = RejectionForm(request.POST)
        if form.is_valid():
            appointment.status = 'rejected'
            appointment.rejection_reason = form.cleaned_data['reason']
            appointment.save()
            messages.success(request, f'Appointment for {appointment.client_name} has been rejected.')
            return redirect('appointments:admin_dashboard')
    return redirect('appointments:admin_dashboard')

@staff_required
def admin_appointment_detail(request, pk):
    """View full appointment details including uploaded images"""
    appointment = get_object_or_404(Appointment, pk=pk)
    rejection_form = RejectionForm()
    return render(request, 'appointments/admin_detail.html', {
        'appointment': appointment,
        'rejection_form': rejection_form,
    })


# ============================================
# CLIENT REVIEW VIEW
# ============================================

@login_required(login_url='appointments:login')
def submit_review(request):
    """Client submits a review"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.client_name = f'{request.user.first_name} {request.user.last_name}'.strip() or request.user.username
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('appointments:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()

    return render(request, 'appointments/submit_review.html', {'form': form})


# ============================================
# ARTIST PROFILE VIEW
# ============================================

def artist_profile(request, pk):
    """Public artist profile/portfolio page"""
    artist = get_object_or_404(Artist, pk=pk, is_active=True)
    portfolio = artist.portfolio_images.all()
    return render(request, 'appointments/artist_profile.html', {
        'artist': artist,
        'portfolio': portfolio,
    })


# ============================================
# ADMIN ARTIST MANAGEMENT VIEWS
# ============================================

@staff_required
def add_artist(request):
    """Admin adds a new artist"""
    if request.method == 'POST':
        form = ArtistForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artist added successfully!')
            return redirect('appointments:landing')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ArtistForm()

    return render(request, 'appointments/artist_form.html', {
        'form': form,
        'title': 'Add New Artist',
    })


@staff_required
def edit_artist(request, pk):
    """Admin edits an existing artist and manages portfolio"""
    artist = get_object_or_404(Artist, pk=pk)
    portfolio = artist.portfolio_images.all()

    if request.method == 'POST':
        form = ArtistForm(request.POST, request.FILES, instance=artist)
        if form.is_valid():
            form.save()

            # Handle multiple portfolio image uploads
            portfolio_files = request.FILES.getlist('portfolio_images')
            for f in portfolio_files:
                PortfolioImage.objects.create(artist=artist, image=f)

            messages.success(request, f'{artist.name} updated successfully!')
            return redirect('appointments:artist_profile', pk=artist.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ArtistForm(instance=artist)

    return render(request, 'appointments/artist_form.html', {
        'form': form,
        'artist': artist,
        'portfolio': portfolio,
        'title': f'Edit {artist.name}',
    })


@staff_required
def delete_artist(request, pk):
    """Admin deletes an artist"""
    artist = get_object_or_404(Artist, pk=pk)
    if request.method == 'POST':
        name = artist.name
        artist.delete()
        messages.success(request, f'{name} has been removed.')
        return redirect('appointments:landing')
    return redirect('appointments:landing')


@staff_required
def delete_portfolio_image(request, pk):
    """Admin deletes a single portfolio image"""
    image = get_object_or_404(PortfolioImage, pk=pk)
    artist_pk = image.artist.pk
    if request.method == 'POST':
        image.image.delete()
        image.delete()
        messages.success(request, 'Portfolio image removed.')
    return redirect('appointments:edit_artist', pk=artist_pk)
