from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Sum
from datetime import date

from employees.models import PerformanceRecord, UploadSession
from dashboard.forms import AnalystCreationForm, ExcelUploadForm
from dashboard.services.excel_service import process_excel_upload

User = get_user_model()


@login_required
def analyst_dashboard(request):
    total_sum = PerformanceRecord.objects.filter(upload_session__is_active=True).aggregate(Sum('actual_earnings'))['actual_earnings__sum'] or 0
    
    context = {
        'total_reports': UploadSession.objects.count(),
        'pending_reviews': 0,
        'processed_incentives': f"₹{total_sum:,.0f}",
        'recent_uploads': UploadSession.objects.all().order_by('-upload_timestamp')[:5],
    }
    return render(request, 'dashboard/analyst/analyst_dashboard.html', context)

@login_required
def analyst_list(request):
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard_home')
        
    analysts = User.objects.filter(role='analyst').order_by('-created_at')
    return render(request, 'dashboard/analyst/analyst_list.html', {'analysts': analysts})

@login_required
def analyst_create(request):
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        form = AnalystCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Data Analyst created successfully!")
            return redirect('analyst_list')
    else:
        form = AnalystCreationForm()
    return render(request, 'dashboard/analyst/analyst_form.html', {'form': form})

@login_required
def upload_excel(request):
    if request.user.role not in ['analyst', 'admin']:
        messages.error(request, "Access denied.")
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            report_date = form.cleaned_data['report_date']
            
            try:
                count = process_excel_upload(
                    excel_file=excel_file,
                    report_date=report_date,
                    uploaded_by=request.user
                )
                messages.success(request, f"Successfully processed {count} records for {report_date}. Incentives have been recalculated.")
                return redirect('analyst_dashboard')
                
            except ValueError as ve:
                messages.error(request, str(ve))
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
    else:
        form = ExcelUploadForm()
    return render(request, 'dashboard/analyst/upload_excel.html', {'form': form})

