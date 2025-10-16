from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def days_overdue(payment_date):
    """Calcula los días de retraso de una cuota"""
    if not payment_date:
        return "N/A"
    
    today = timezone.localdate()
    if payment_date < today:
        delta = today - payment_date
        return f"{delta.days} días"
    else:
        return "Hoy"
