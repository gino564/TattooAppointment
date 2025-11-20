from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # PUBLIC PAGES (NO LOGIN REQUIRED)
    path('landing/', views.landing_page, name='landing'),# NEW: Main homepage
    path('enquiry/submit/', views.enquiry_submit, name='enquiry_submit'),  # NEW: Handle enquiry form
    
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
]