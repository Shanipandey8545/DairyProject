# utils.py (or inside views.py)
from dateutil.relativedelta import relativedelta
from django.utils import timezone

def compute_expiry(plan_type):
    now = timezone.now()
    if plan_type == 'Free for 7 Days':
        return now + relativedelta(days=7)
    if plan_type == 'Monthly':
        return now + relativedelta(months=1)
    if plan_type == 'Quarterly':
        return now + relativedelta(months=3)
    if plan_type == 'Six Months':
        return now + relativedelta(months=6)
    if plan_type == 'Yearly':
        return now + relativedelta(years=1)
    return now  # fallback
