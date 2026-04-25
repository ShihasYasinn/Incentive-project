import pandas as pd
from django.db import transaction
from django.contrib.auth import get_user_model

from employees.models import PerformanceRecord, UploadSession
from commons.utils.earning_calculation import calculate_net_earning
from commons.utils.incentive_service import calculate_and_store_all_incentives

User = get_user_model()

def process_excel_upload(excel_file, report_date, uploaded_by):
    """
    Processes the uploaded Excel file, creates performance records, 
    and triggers incentive recalculation.
    Returns the number of records created.
    """
    # 1. READ AND MERGE ALL SHEETS
    sheets_dict = pd.read_excel(excel_file, sheet_name=None)
    full_df = None
    
    for _, df in sheets_dict.items():
        df.columns = [str(c).strip() for c in df.columns]
        if 'Emp ID' in df.columns:
            # Clean Emp ID column to ensure they match
            df['Emp ID'] = df['Emp ID'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
            
            if full_df is None:
                full_df = df
            else:
                # Merge on Emp ID
                common_cols = [c for c in ['Emp ID', 'Emp Details', 'Branch'] if c in full_df.columns and c in df.columns]
                full_df = pd.merge(full_df, df, on=common_cols, how='outer')
    
    if full_df is None:
        raise ValueError("No 'Emp ID' column found in any sheet.")
    
    # 2. PRE-FETCH USERS
    emp_ids = full_df['Emp ID'].dropna().unique().tolist()
    existing_users = {u.employee_id: u for u in User.objects.filter(employee_id__in=emp_ids)}
    
    records_to_create = []
    
    with transaction.atomic():
        # 3. CREATE AUDIT SESSION
        session = UploadSession.objects.create(
            uploaded_by=uploaded_by,
            file_name=excel_file.name,
            report_date=report_date
        )
        
        # 4. DEACTIVATE PREVIOUS DATA FOR THIS DATE
        UploadSession.objects.filter(report_date=report_date).exclude(id=session.id).update(is_active=False)
        
        # 5. PROCESS ROWS
        for _, row in full_df.iterrows():
            emp_id = str(row.get('Emp ID', '')).strip()
            if not emp_id or emp_id.lower() == 'nan': continue
            if emp_id.endswith('.0'): emp_id = emp_id[:-2]
            
            user = existing_users.get(emp_id)
            if not user:
                # Auto-create user if missing
                user = User.objects.create(
                    employee_id=emp_id,
                    email=f"emp_{emp_id}@erp.com",
                    full_name=str(row.get('Emp Details', f"Emp {emp_id}")),
                    role='employee'
                )
                existing_users[emp_id] = user
                
            # Column detection helpers (case-insensitive)
            def get_col_val(keywords, default_val=0, is_int=True):
                target_col = None
                for c in full_df.columns:
                    if all(k.upper() in str(c).upper() for k in keywords):
                        target_col = c
                        break
                
                if target_col and pd.notnull(row[target_col]):
                    try:
                        return int(row[target_col]) if is_int else float(row[target_col])
                    except:
                        return default_val
                return default_val

            # Financial metrics detection
            earnings_col = next((c for c in full_df.columns if 'EARNING' in str(c).upper()), None)
            gross_val = float(row[earnings_col]) if earnings_col and pd.notnull(row[earnings_col]) else 0.0
            
            # Service counts detection
            free_count = get_col_val(['FREE'])
            paid_count = get_col_val(['PAID'])
            rr_count = get_col_val(['RR'])
            
            # Handle Wheel Alignment / Lathe
            wa_val = get_col_val(['WHEEL', 'LATHE'], is_int=False)
            
            # Detect Slab (Yes/No columns)
            def get_bool_col(keywords):
                for c in full_df.columns:
                    if all(k.upper() in str(c).upper() for k in keywords):
                        val = str(row[c]).strip().upper()
                        return val in ['YES', 'Y', 'TRUE', '1']
                return False

            above_150 = get_bool_col(['ABOVE', '150'])
            below_150 = get_bool_col(['BELOW', '150'])
            
            # If 'Above' is Yes, it's above. If 'Below' is Yes, it's below.
            # If both are missing or No, default to below (as per model default).
            is_above_val = True if above_150 else False
            if not above_150 and below_150:
                is_above_val = False
            
            # Calculate Net Earning
            net_val = calculate_net_earning(
                gross_earning=gross_val,
                wheel_alignment_lathe=wa_val,
                free_count=free_count,
                paid_count=paid_count,
                rr_count=rr_count
            )

            # Build Record
            record = PerformanceRecord(
                upload_session=session,
                employee=user,
                date=report_date,
                total_earnings=gross_val,
                actual_earnings=net_val,
                leave_status='L' if str(row.get('Leave', '')).strip().upper() == 'L' else 'P',
                free=free_count,
                paid=paid_count,
                rr=rr_count,
                wheel_alignment_lathe=wa_val,
                is_above_150=is_above_val,
                vehicle_count=free_count + paid_count + rr_count
            )
            records_to_create.append(record)
            
        # 6. BULK CREATE
        PerformanceRecord.objects.bulk_create(records_to_create)
        
        # 7. Recalculate Incentives for the entire month
        calculate_and_store_all_incentives(report_date.year, report_date.month)
        
    return len(records_to_create)
