from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # PUBLIC PAGES (NO LOGIN REQUIRED)
    path('landing/', views.landing_page, name='landing'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Protected appointment URLs (REQUIRE LOGIN)
    path('appointments/', views.index, name='index'),  # Changed from '' to 'appointments/'
    path('appointments/list-fbv/', views.appointment_list_fbv, name='list-fbv'),
    path('appointments/list-cbv/', views.AppointmentListCBV.as_view(), name='list-cbv'),
    
    # Edit and Delete URLs
    path('appointments/edit/<int:pk>/', views.appointment_edit, name='edit'),
    path('appointments/delete/<int:pk>/', views.appointment_delete, name='delete'),

    # Client booking
    path('book/', views.book_session, name='book_session'),

    # Client review
    path('review/', views.submit_review, name='submit_review'),

    # Artist profile (public)
    path('artist/<int:pk>/', views.artist_profile, name='artist_profile'),

    # Admin panel URLs (staff only)
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/approve/<int:pk>/', views.admin_approve, name='admin_approve'),
    path('admin-panel/reject/<int:pk>/', views.admin_reject, name='admin_reject'),
    path('admin-panel/detail/<int:pk>/', views.admin_appointment_detail, name='admin_detail'),
]