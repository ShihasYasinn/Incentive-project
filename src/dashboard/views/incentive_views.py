from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from employees.models import MonthlyIncentive


@login_required
def monthly_incentive_report(request):
    month_val = request.GET.get('month')
    year_val = request.GET.get('year')
    
    if month_val and year_val:
        try:
            report_month = date(int(year_val), int(month_val), 1)
            incentives = MonthlyIncentive.objects.filter(month=report_month).order_by('employee__full_name')
        except:
            incentives = MonthlyIncentive.objects.all().order_by('-month', 'employee__full_name')
    else:
        incentives = MonthlyIncentive.objects.all().order_by('-month', 'employee__full_name')
        
    # Prepare months and years for filter dropdowns
    months_list = [(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    years_list = range(2024, date.today().year + 2)
    
    return render(request, 'dashboard/incentives/report.html', {
        'incentives': incentives,
        'current_month': int(month_val) if month_val else None,
        'current_year': int(year_val) if year_val else None,
        'months': months_list,
        'years': years_list
    })