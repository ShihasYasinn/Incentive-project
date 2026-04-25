from decimal import Decimal

def calculate_net_earning(gross_earning, wheel_alignment_lathe, free_count, paid_count, rr_count):
    """
    Calculates net earning based on gross earning and deductions.
    
    Deductions:
    1. Wheel Alignment/Lathe amount (direct deduction)
    2. External water service: ₹50 per service (Free + Paid + RR)
    
    Formula:
    Net = Gross - (WheelAlignmentLathe + (150 * (Free + Paid + RR)))
    """
    # Convert to Decimal for precise financial calculations
    gross_earning = Decimal(str(gross_earning))
    wheel_alignment_lathe = Decimal(str(wheel_alignment_lathe))
    
    total_service_count = free_count + paid_count + rr_count
    # Using 50 based on example: 150 total for 3 services (1 Free + 1 Paid + 1 RR)
    service_deduction = Decimal(str(150 * total_service_count))
    
    total_deduction = wheel_alignment_lathe + service_deduction
    net_earning = gross_earning - total_deduction
    
    return net_earning
