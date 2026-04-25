from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('dashboard_home')
        elif request.user.role == 'analyst':
            return redirect('analyst_dashboard')
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'admin':
                    return redirect('dashboard_home')
                elif user.role == 'analyst':
                    return redirect('analyst_dashboard')
                return redirect('dashboard_home')
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

@login_required
def dashboard_home(request):
    if request.user.role == 'analyst':
        return redirect('analyst_dashboard')
        
    context = {
        'total_users': User.objects.count(),
        'admin_count': User.objects.filter(role='admin').count(),
        'employee_count': User.objects.filter(role='employee').count(),
        'analyst_count': User.objects.filter(role='analyst').count(),
        'recent_users': User.objects.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/index.html', context)