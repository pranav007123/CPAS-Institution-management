from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Get a value from a dict using a variable key."""
    return d.get(key, [])
