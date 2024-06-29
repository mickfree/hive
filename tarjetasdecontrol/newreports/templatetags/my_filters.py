from django import template

register = template.Library()

@register.filter
def get_day(value, arg):
    return value.get(arg, 0)
