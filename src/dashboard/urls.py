from django.urls import path
from .views import AdminLoginView, DashboardHomeView, AnalystListView, AnalystCreateView, AnalystDashboardView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', DashboardHomeView.as_view(), name='dashboard_home'),
    path('analyst/', AnalystDashboardView.as_view(), name='analyst_dashboard'),
    path('analysts/', AnalystListView.as_view(), name='analyst_list'),
    path('analysts/add/', AnalystCreateView.as_view(), name='analyst_add'),
]
