from django.contrib.auth.decorators import login_required
from ..models import *
from ..forms import *

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user, logout
from django.contrib import messages


@login_required
def roles(request):
    user = get_user(request)
    department = user.profile.member.user_department
    context = {
        "department": department
    }
    return render(request, 'user_department/roles.html', context)


def assign_preparation_role(request):
    user = get_user(request)
    department = user.profile.member.user_department
    members = department.get_members()
    if request.method == "POST":
        for member in members:
            department_member = member.profile.department_member
            department_member.plan_preparation = False
            department_member.save()

        department_member_id = request.POST["plan_preparation"]
        department_member = DepartmentMember.objects.get(id=department_member_id)
        department_member.plan_preparation = True
        department_member.save()
        messages.info(request, f'Plan Preparation Role Assigned to "{department.get_plan_preparation_member()}"')
        return redirect('plan:roles')