from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils import timezone
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import User, UserSession

class CustomLoginView(LoginView):
    """
    Custom login view with session tracking
    """
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        # Get user
        user = form.get_user()
        
        # Check if account is locked
        if user.account_locked:
            messages.error(self.request, 'Your account is locked. Contact administrator.')
            return redirect('login')
        
        # Log the login
        response = super().form_valid(form)
        
        # Create session record
        UserSession.objects.create(
            user=user,
            session_key=self.request.session.session_key,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
        )
        
        # Update user online status
        user.is_online = True
        user.last_login_ip = self.get_client_ip()
        user.login_attempts = 0
        user.save()
        
        messages.success(self.request, f'Welcome back, {user.get_full_name()}!')
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def form_invalid(self, form):
        # Track failed login attempts
        username = form.cleaned_data.get('username')
        try:
            user = User.objects.get(username=username)
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.account_locked = True
                messages.warning(self.request, 'Account locked due to too many failed attempts')
            user.save()
        except User.DoesNotExist:
            pass
        
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)


@login_required
def custom_logout(request):
    """
    Custom logout to update session
    """
    # Update session record
    try:
        session = UserSession.objects.filter(
            user=request.user, 
            session_key=request.session.session_key,
            is_active=True
        ).latest('login_time')
        session.logout_time = timezone.now()
        session.is_active = False
        session.save()
    except UserSession.DoesNotExist:
        pass
    
    # Update user online status
    request.user.is_online = False
    request.user.save()
    
    logout(request)
    messages.info(request, 'You have been logged out successfully')
    return redirect('login')


@login_required
def dashboard(request):
    """
    Main dashboard based on user role
    """
    context = {
        'user': request.user,
        'today': timezone.now().date(),
    }
    
    # Role-specific dashboard data
    if request.user.role == 'admin':
        # Admin dashboard data
        from patients.models import Patient
        from consultations.models import Consultation
        
        context.update({
            'total_patients': Patient.objects.count(),
            'today_consultations': Consultation.objects.filter(
                visit_date=timezone.now().date()
            ).count(),
            'recent_patients': Patient.objects.order_by('-created_at')[:5],
            'recent_consultations': Consultation.objects.order_by('-created_at')[:5],
        })
    
    elif request.user.role == 'doctor':
        # Doctor dashboard - show today's appointments
        from consultations.models import Consultation
        context['my_appointments'] = Consultation.objects.filter(
            doctor=request.user,
            visit_date=timezone.now().date()
        ).select_related('patient')
    
    # Add more role-specific dashboards
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile(request):
    """
    User profile view and edit
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get user sessions
    sessions = UserSession.objects.filter(user=request.user)[:10]
    
    context = {
        'form': form,
        'sessions': sessions,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def user_list(request):
    """
    Admin view for managing users
    """
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})