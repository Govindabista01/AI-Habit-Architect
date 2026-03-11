from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

urlpatterns = [
    # Homepage redirect
    path('', home_redirect, name='home'),
    
    # Admin panel
    path('admin/', admin.site.urls),

    # Web Pages (HTML)
    path('accounts/', include('accounts.urls')),
    path('habits/', include('habits.urls')),
    path('predictions/', include('predictions.urls')),
    path('analytics/', include('analytics.urls')),  # NEW LINE
    
    # REST APIs
    path('api/', include('habits.api_urls')),
    path('api/auth/', include('rest_framework.urls')),
]