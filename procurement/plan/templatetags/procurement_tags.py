from django import template
import json

register = template.Library()

@register.filter(name="comma_separator")
def comma_separator(value):
	if isinstance(value, int):
		return f'{value:,}' + ' UGX'
	return value


@register.filter(name="total_cost")
def total_cost(item):
	return item.quantity * item.unit_cost


@register.filter(name="format_date")
def format_date(date):
	date = date.strftime("%d/%b/%Y %H:%M:%S")
	return date


@register.filter(name='add_css')
def add_css(field, css):
	return field.as_widget(attrs={"class":css})


@register.filter(name='add_attrs')
def add_attrs(field, attrs):
	attrs = json.loads(attrs)
	return field.as_widget(attrs=attrs)
	
