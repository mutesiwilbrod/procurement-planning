from django import template
import json

register = template.Library()

@register.filter(name="comma_separator")
def comma_separator(value):
	if isinstance(value, int):
		return f'{value:,}'
	return value


@register.filter(name="total_cost")
def total_cost(item):
	return item.quantity * item.unit_cost


@register.filter(name="format_date")
def format_date(date):
	date = date.strftime("%d/%b/%Y %H:%M:%S")
	return date


@register.filter(name="html_date")
def html_date(date):
	date = date.strftime("%Y-%m-%d")
	return date


@register.filter(name='add_css')
def add_css(field, css):
	return field.as_widget(attrs={"class":css})


@register.filter(name='add_attrs')
def add_attrs(field, attrs):
	attrs = json.loads(attrs)
	return field.as_widget(attrs=attrs)
	

@register.filter(name="consolidated_plan_cost")
def consolidated_plan_cost(plans):
	return sum([plan.estimated_cost for plan in plans])


@register.filter(name="consolidated_source_of_funding")
def consolidated_source_of_funding(plans):
	if len(plans):
		return set([plan.source_of_funding for plan in plans])
	return '....'


@register.filter(name="consolidated_procurement_method")
def consolidated_procurement_method(plan_cost):
	if plan_cost < 1000000:
		return 'Micro Procurement'
	elif plan_cost < 10000000:
		return 'RFQ'
	else:
		return 'International Bidding'