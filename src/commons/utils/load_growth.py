from decimal import Decimal
from django.db.models import Sum, Q
from datetime import date

from employees.models import PerformanceRecord, LoadGrowthSlab


def calculate_load_growth_adjustment(employee, year, month, eligible_incentive):
    """
    Calculates the Load Growth Adjustment for an employee's incentive using dynamic slabs.
    """
    
    # 1. Get performance records for current month
    current_records = PerformanceRecord.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month,
        upload_session__is_active=True
    )
    
    if not current_records.exists():
        return Decimal('0.00'), 0.0, "No performance data for current month"

    # Current earnings sum
    current_earnings = current_records.aggregate(Sum('actual_earnings'))['actual_earnings__sum'] or Decimal('0.00')
    is_above_150 = current_records.filter(is_above_150=True).exists()
    slab_val = 'ABOVE' if is_above_150 else 'BELOW'

    # 2. Find the same dates in the previous year
    active_days = list(current_records.values_list('date__day', flat=True))
    
    prev_year = year - 1
    prev_records = PerformanceRecord.objects.filter(
        employee=employee,
        date__year=prev_year,
        date__month=month,
        date__day__in=active_days,
        upload_session__is_active=True
    )
    
    prev_earnings = prev_records.aggregate(Sum('actual_earnings'))['actual_earnings__sum'] or Decimal('0.00')

    # 3. Calculate Growth Percentage
    if prev_earnings <= 0:
        return Decimal('0.00'), 0.0, "No historical data for comparison"

    growth_percent = float(((current_earnings - prev_earnings) / prev_earnings) * 100)
    
    adjustment = Decimal('0.00')
    note = f"Growth: {growth_percent:.2f}%"

    # 4. Find matching Load Growth Slab
    # Logic: Match by slab type (ABOVE/BELOW/BOTH) and find the most specific growth range
    
    # First try: Range match (where growth is between min and max)
    rule = LoadGrowthSlab.objects.filter(
        Q(load_slab=slab_val) | Q(load_slab='BOTH'),
        min_growth_percent__lte=growth_percent,
        max_growth_percent__gte=growth_percent
    ).first()

    if not rule:
        # Second try: Open-ended high growth (where max is null)
        rule = LoadGrowthSlab.objects.filter(
            Q(load_slab=slab_val) | Q(load_slab='BOTH'),
            min_growth_percent__lte=growth_percent,
            max_growth_percent__isnull=True
        ).order_by('-min_growth_percent').first()

    if not rule:
        # Third try: Open-ended low growth/degrowth (where min is null)
        rule = LoadGrowthSlab.objects.filter(
            Q(load_slab=slab_val) | Q(load_slab='BOTH'),
            min_growth_percent__isnull=True,
            max_growth_percent__gte=growth_percent
        ).order_by('max_growth_percent').first()

    # 5. Apply the rule if found
    if rule:
        if rule.incentive_amount > 0:
            adjustment = rule.incentive_amount
            note += f" ({rule.get_load_slab_display()} bonus: +₹{adjustment})"
        elif rule.deduction_percent > 0:
            deduction = eligible_incentive * (rule.deduction_percent / Decimal('100'))
            adjustment = -deduction
            note += f" ({rule.deduction_percent}% degrowth deduction: -₹{deduction:.2f})"
        else:
            note += " (No adjustment for this tier)"
    else:
        note += " (No matching growth slab)"

    return adjustment, growth_percent, note
