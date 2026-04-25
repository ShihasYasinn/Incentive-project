from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard_home, name='dashboard_home'),
    path('analyst/', views.analyst_dashboard, name='analyst_dashboard'),
    path('analyst/upload/', views.upload_excel, name='upload_excel'),
    path('analysts/', views.analyst_list, name='analyst_list'),
    path('analysts/add/', views.analyst_create, name='analyst_add'),
    
    # Incentives Management
    path('incentives/slabs/', views.slab_list, name='slab_list'),
    path('incentives/slabs/add/', views.slab_create, name='slab_create'),
    path('incentives/slabs/<int:pk>/edit/', views.slab_edit, name='slab_edit'),
    path('incentives/slabs/<int:pk>/delete/', views.slab_delete, name='slab_delete'),
    
    # Load Growth Slabs
    path('incentives/growth-slabs/add/', views.load_growth_slab_create, name='growth_slab_create'),
    path('incentives/growth-slabs/<int:pk>/edit/', views.load_growth_slab_edit, name='growth_slab_edit'),
    path('incentives/growth-slabs/<int:pk>/delete/', views.load_growth_slab_delete, name='growth_slab_delete'),
    
    path('incentives/targets/', views.target_list, name='target_list'),
    path('incentives/targets/add/', views.target_create, name='target_create'),
    path('incentives/targets/<int:pk>/edit/', views.target_edit, name='target_edit'),
    path('incentives/targets/<int:pk>/delete/', views.target_delete, name='target_delete'),
    
    path('incentives/reports/', views.monthly_incentive_report, name='incentive_report'),
]
