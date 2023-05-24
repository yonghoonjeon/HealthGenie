from django import template
import json

register = template.Library()

@register.filter
def load_json(value):
    return json.loads(value)