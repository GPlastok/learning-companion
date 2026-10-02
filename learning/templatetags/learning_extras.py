from django import template

register = template.Library()


@register.filter
def duration(minutes):
    """Whole minutes as "1 h 30 min", "2 h" or "45 min" (D24)."""
    hours, rest = divmod(minutes, 60)
    if hours and rest:
        return f"{hours} h {rest} min"
    if hours:
        return f"{hours} h"
    return f"{rest} min"
