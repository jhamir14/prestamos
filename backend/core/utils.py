from datetime import timedelta

def generate_payment_schedule(start_date, num_installments, frequency):
    schedule = []
    current_date = start_date
    count = 0
    
    while count < num_installments:
        if frequency == 'Diario':
            current_date += timedelta(days=1)
            # 0=Monday, 6=Sunday. Skip Sunday.
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
        elif frequency == 'Semanal':
            current_date += timedelta(weeks=1)
        
        schedule.append(current_date)
        count += 1
    
    return schedule
