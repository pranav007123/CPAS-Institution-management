from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)

@register.filter
def get_sum(results_dict):
    if not results_dict or not isinstance(results_dict, dict):
        return 0
    return sum(v for v in results_dict.values() if v is not None)
