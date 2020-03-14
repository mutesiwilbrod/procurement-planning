from .models import *


def get_entity_departments(entity):
    user_departments = []
    for programme in entity.programmes():
        for sub_programme in programme.sub_programmes():
            user_departments.extend(sub_programme.user_departments())
    return user_departments


def get_entity_plans(entity):
    user_departments = get_entity_departments(entity)
    entity_plans = []
    for department in user_departments:
        entity_plans.extend(Plan.objects.filter(user_department=department))
    return entity_plans


def get_consolidated_plans(entity):
    departments = get_entity_departments(entity)
    expenses = Expense.objects.all()
    consolidated_plans = []
    for expense in expenses:
        consolidated_plans.append((expense, expense.pdu_approved_plans_for_departments(departments)))
    return consolidated_plans