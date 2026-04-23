from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, CreateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import AnalystCreationForm

User = get_user_model()

class AdminLoginView(LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.role == 'admin':
            return reverse_lazy('dashboard_home')
        elif user.role == 'analyst':
            return reverse_lazy('analyst_dashboard')
        return reverse_lazy('dashboard_home')

@method_decorator(login_required, name='dispatch')
class DashboardHomeView(TemplateView):
    template_name = 'dashboard/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'analyst':
            return redirect('analyst_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If an analyst somehow gets here, we might want to redirect them or show limited data
        # But for now, let's keep it as is or handle it in the view
        context['total_users'] = User.objects.count()
        context['admin_count'] = User.objects.filter(role='admin').count()
        context['employee_count'] = User.objects.filter(role='employee').count()
        context['analyst_count'] = User.objects.filter(role='analyst').count()
        context['recent_users'] = User.objects.order_by('-created_at')[:5]
        return context

@method_decorator(login_required, name='dispatch')
class AnalystDashboardView(TemplateView):
    template_name = 'dashboard/analyst_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Placeholder data for analyst dashboard
        context['total_reports'] = 124
        context['pending_reviews'] = 12
        context['processed_incentives'] = "₹4.5L"
        return context

@method_decorator(login_required, name='dispatch')
class AnalystListView(ListView):
    model = User
    template_name = 'dashboard/analyst_list.html'
    context_object_name = 'analysts'

    def get_queryset(self):
        return User.objects.filter(role='analyst').order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class AnalystCreateView(CreateView):
    model = User
    form_class = AnalystCreationForm
    template_name = 'dashboard/analyst_form.html'
    success_url = reverse_lazy('analyst_list')

    def form_valid(self, form):
        messages.success(self.request, "Data Analyst created successfully!")
        return super().form_valid(form)
