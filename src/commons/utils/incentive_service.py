from decimal import Decimal
from django.db.models import Sum, Q
from django.contrib.auth import get_user_model
from datetime import date

from employees.models import MonthlyIncentive, PerformanceRecord, MonthlyTarget, IncentiveSlab

def calculate_monthly_incentive(employee, year, month):
    """
    Calculates the monthly incentive for an employee based on the simplified target/slab system.
    Formula: Incentive = Incentive % (from Slab) * Monthly Target
    (Based on user's example: 'if 110% of target is achieved then incentive amount will be 2% of the target')
    """
    # 1. Aggregate monthly performance
    records = PerformanceRecord.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month,
        upload_session__is_active=True
    )
    
    if not records.exists():
        return Decimal('0.00'), "No records found for this month"

    perf_data = records.aggregate(
        total_labour=Sum('actual_earnings')
    )
    
    # 2. Determine Slab (Above/Below 150)
    is_above_150 = records.filter(is_above_150=True).exists()
    slab_val = 'ABOVE' if is_above_150 else 'BELOW'

    total_labour = perf_data['total_labour'] or Decimal('0.00')

    if total_labour <= 0:
        return Decimal('0.00'), "No labour achieved"

    # 3. Get Target (Common for all employees)
    target = MonthlyTarget.objects.filter(
        month__year=year,
        month__month=month
    ).first()
    
    if not target or target.target_amount <= 0:
        return Decimal('0.00'), "No target defined for this month"
    
    target_amount = target.target_amount
    achievement_percent = (total_labour / target_amount) * 100

    details = {
        'total_labour': total_labour,
        'target_amount': target_amount,
        'is_above_150': is_above_150,
        'slab': slab_val,
        'achievement_percent': achievement_percent,
        'breakdown': []
    }

    # 4. Find matching Incentive Slab (Specific or BOTH)
    # Try finding a range rule first (where achievement is between min and max)
    slab_rule = IncentiveSlab.objects.filter(
        Q(load_slab=slab_val) | Q(load_slab='BOTH'),
        min_achievement_percent__lte=achievement_percent,
        max_achievement_percent__gte=achievement_percent
    ).first()

    if not slab_rule:
        # Fallback to open-ended rules (where max is null)
        slab_rule = IncentiveSlab.objects.filter(
            Q(load_slab=slab_val) | Q(load_slab='BOTH'),
            min_achievement_percent__lte=achievement_percent,
            max_achievement_percent__isnull=True
        ).order_by('-min_achievement_percent').first()
    
    if not slab_rule:
        return Decimal('0.00'), f"No incentive slab reached (Achievement: {achievement_percent:.1f}%)"

    # 5. Calculate Base Incentive (Slab-based)
    slab_incentive = (slab_rule.incentive_percent / 100) * target_amount
    
    # 6. Calculate Efficiency Bonus (Based on Earning/Vehicle Count)
    total_vehicles = records.aggregate(total=Sum('vehicle_count'))['total'] or 0
    efficiency_bonus = Decimal('0.00')
    
    if total_vehicles > 0:
        ratio = total_labour / Decimal(total_vehicles)
        if ratio > 11000:
            efficiency_bonus = Decimal('6000.00')
        elif ratio > 10500:
            efficiency_bonus = Decimal('5000.00')
            
    total_incentive = slab_incentive + efficiency_bonus

    # 7. Calculate Load Growth Adjustment (New logic)
    from commons.utils.load_growth import calculate_load_growth_adjustment
    growth_adj, growth_pct, growth_note = calculate_load_growth_adjustment(
        employee, year, month, total_incentive
    )
    
    final_incentive = total_incentive + growth_adj

    details.update({
        'incentive_percent': slab_rule.incentive_percent,
        'slab_incentive': slab_incentive,
        'efficiency_bonus': efficiency_bonus,
        'total_vehicles': total_vehicles,
        'earning_per_vehicle': total_labour / Decimal(total_vehicles) if total_vehicles > 0 else 0,
        'load_growth_adjustment': growth_adj,
        'growth_percentage': growth_pct,
        'growth_note': growth_note,
        'incentive_amount': final_incentive,
        'matched_rule': str(slab_rule)
    })
    
    return final_incentive, details



def calculate_and_store_all_incentives(year, month):
    """
    Calculates and stores monthly incentives for all employees for a given month.
    """
    User = get_user_model()
    report_date = date(year, month, 1)
    # Only calculate for active employees
    employees = User.objects.filter(role='employee', is_active=True)
    results = []

    for employee in employees:
        incentive_amount, details = calculate_monthly_incentive(employee, year, month)
        
        if isinstance(details, dict):
            # Successfully calculated
            MonthlyIncentive.objects.update_or_create(
                employee=employee,
                month=report_date,
                defaults={
                    'total_earnings': details['total_labour'],
                    'target_amount': details['target_amount'],
                    'achievement_percent': details['achievement_percent'],
                    'total_vehicles': details['total_vehicles'],
                    'incentive_percent': details['incentive_percent'],
                    'efficiency_bonus': details['efficiency_bonus'],
                    'incentive_amount': incentive_amount,
                    'slab_type': details['slab']
                }
            )
            results.append({
                'employee': employee.full_name or employee.email,
                'status': 'Success',
                'amount': float(incentive_amount)
            })
        else:
            # Skip or record failure if needed. Here we just record it in the returned results.
            results.append({
                'employee': employee.full_name or employee.email,
                'status': 'Skipped',
                'reason': str(details)
            })
            
    return results
