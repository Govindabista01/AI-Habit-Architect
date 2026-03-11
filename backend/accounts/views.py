from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import UserProfile


def register_view(request):
    """User registration page"""

    # If user is already logged in, send to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # Save user
            user = form.save()

            # Profile is created automatically by signal in models.py
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You are now logged in.')

            # Log user in automatically after registration
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Registration failed. Please fix the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login page"""

    # If user is already logged in, send to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}.')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    """User profile page"""
    user = request.user
    habits = user.habits.filter(is_active=True)
    total_habits = habits.count()
    active_streaks = habits.filter(current_streak__gt=0).count()

    context = {
        'user': user,
        'total_habits': total_habits,
        'active_streaks': active_streaks,
    }

    return render(request, 'accounts/profile.html', context)