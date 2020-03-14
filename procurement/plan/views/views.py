from django.contrib.auth.decorators import login_required
from ..models import *
from ..forms import *
from ..utilities import *

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, get_user
from django.http import JsonResponse
from django.core.serializers import serialize
import json

from datetime import datetime


@login_required
def plan(request):
    if request.method == "GET":
        user = get_user(request)
        department = user.profile.member.user_department
        form = PlanItemForm()
        form.fields['chart_of_account'].choices = Expense.generate_field_choices(Expense)
        form.fields['type_of_procurement'].choices = ProcurementType.generate_field_choices(ProcurementType)
        context = {
            "department": department, "form": form
        }
        return render(request, 'user_department/plan.html', context)


# USER DEPARTMENT MEMBER
@login_required
def add_plan(request):
    user = get_user(request)
    department = user.profile.member.user_department
    if request.method == "POST":
        form = PlanItemForm(request.POST)
        form.fields["chart_of_account"].choices = Expense.generate_field_choices(Expense)
        form.fields["type_of_procurement"].choices = ProcurementType.generate_field_choices(ProcurementType)
        # validate form
        if form.is_valid():
            # save plan item
            chart_of_account = Expense.objects.get(id=request.POST["chart_of_account"])
            type_of_procurement = ProcurementType.objects.get(id=request.POST["type_of_procurement"])
            subject_of_procurement = request.POST["subject_of_procurement"]
            quantity = request.POST["quantity"]
            unit = request.POST["unit"]
            estimated_cost = request.POST["estimated_cost"]
            source_of_funding = request.POST["source_of_funding"]
            date_required_q1, date_required_q2, date_required_q3, date_required_q4 = False, False, False, False
            if request.POST.get("date_required_q1"): date_required_q1 = True
            if request.POST.get("date_required_q2"): date_required_q2 = True
            if request.POST.get("date_required_q3"): date_required_q3 = True
            if request.POST.get("date_required_q4"): date_required_q4 = True

            # save plan
            plan = Plan(
                chart_of_account=chart_of_account,
                subject_of_procurement=subject_of_procurement,
                type_of_procurement=type_of_procurement,
                quantity=quantity,
                unit_of_measure=unit,
                estimated_cost=estimated_cost,
                source_of_funding=source_of_funding,
                date_required_q1=date_required_q1,
                date_required_q2=date_required_q2,
                date_required_q3=date_required_q3,
                date_required_q4=date_required_q4,
                user_department = department,
                date_prepared = datetime.now()
            )
            if (department.total_amount_planned() + int(plan.estimated_cost)) > department.budget_sealing:
                messages.warning(request, "Insufficient Funds!")
                return redirect('plan:plan')
            plan.save()

            # save action
            action = PlanAction(action="Prepared", plan=plan, member=user.profile.member)
            action.save()
            messages.info(request, "Prepared Plan")
        return redirect('plan:plan')


@login_required
def edit_plan(request, id):
    plan = Plan.objects.get(id=id)

    if request.method == "POST":
        user = get_user(request)
        department = user.profile.member.user_department
        total_amount_planned = department.total_amount_planned() - int(plan.estimated_cost)
        # TODO - Validate this data/form before saving
        plan.chart_of_account = Expense.objects.get(id=request.POST["chart_of_account"])
        plan.subject_of_procurement = request.POST["subject_of_procurement"]
        plan.type_of_procurement = ProcurementType.objects.get(id=request.POST["type_of_procurement"])
        plan.quantity = request.POST["quantity"]
        plan.unit_of_measure = request.POST["unit_of_measure"]
        plan.estimated_cost = request.POST["estimated_cost"]
        plan.source_of_funding = request.POST["source_of_funding"]
        date_required_q1, date_required_q2, date_required_q3, date_required_q4 = False, False, False, False
        if request.POST.get("date_required_q1"): date_required_q1 = True
        if request.POST.get("date_required_q2"): date_required_q2 = True
        if request.POST.get("date_required_q3"): date_required_q3 = True
        if request.POST.get("date_required_q4"): date_required_q4 = True
        plan.date_required_q1 = date_required_q1
        plan.date_required_q2 = date_required_q2
        plan.date_required_q3 = date_required_q3
        plan.date_required_q4 = date_required_q4
        if (total_amount_planned + int(plan.estimated_cost)) > department.budget_sealing:
            messages.warning(request, "Insufficient Funds!")
            return redirect("plan:plan")
        plan.save()
        # save action
        action = PlanAction(action="Edited", plan=plan, member=user.profile.member)
        action.save()
        messages.info(request, "Updated Plan")
        return redirect("plan:plan")
    elif request.method == "GET":
        expenses = Expense.generate_field_choices(Expense)
        procurement_types = ProcurementType.generate_field_choices(ProcurementType)
        context = {"plan_item": plan, "plan": plan, "expenses":expenses, "procurement_types":procurement_types}
        return render(request, 'user_department/edit-plan.html', context)


@login_required
def remove_plan(request):
    if request.method == "POST":
        plan_id = request.POST.get("plan_item_id")
        plan = Plan.objects.get(id=plan_id)
        if plan:
            messages.info(request, "Removed Plan")
            plan.delete()
        else:
            messages.info(request, "Failed to remove plan")
        return redirect("plan:plan")


@login_required
def finish_plan_preparation(request):
    if request.method == "POST":
        password = request.POST["password"]
        user = get_user(request)
        department = user.profile.member.user_department
        user = authenticate(username=user.email, password=password)
        if user:
            department.plan_prepared = True
            department.plan_prepared_date = datetime.now()
            department.save()
            messages.success(request, "Plans Prepared")
        else:
            messages.warning(request, "Invalid Password!")
        return redirect("plan:plan")


# MEMBER, HEAD OF DEPARTMENT AND HEAD OF PDU
@login_required
def comment(request, id):
    if request.method == "POST":
        comment = request.POST["comment"]
        user = get_user(request)
        plan = Plan.objects.get(id=id)
        if plan:
            comment = PlanComment(comment=comment, plan=plan, member=user.profile.member)
            comment.save()

            # save action
            action = PlanAction(action="Commented", plan=plan, member=user.profile.member)
            action.save()
            messages.info(request, "Comment Posted")
        return redirect("plan:plan_details", id=plan.id)


@login_required
def plan_details(request, id):
    plan = Plan.objects.get(id=id)
    context = {"plan": plan}
    return render(request, 'user_department/plan-details.html', context)


# HEAD OF DEPARTMENT
# AJAX
@login_required
def hod_approve_plan(request, id):
    success = {
        "message": "SUCCESS",
        "data": None
    }
    error = {
        "message": "ERROR",
        "data": None
    }
    if request.method == "GET":
        user = get_user(request)
        department = user.profile.member.user_department
        plan = Plan.objects.get(id=id)

        if plan in department.plans():
            if plan.hod_approved:
                # update plan
                plan.hod_approved = False
                plan.date_hod_approved = None
                plan.save()
                # save action
                action = PlanAction(action="HOD Unapproved", plan=plan, member=user.profile.member)
                action.save()
                # make json return
                serialized_plan = json.loads(serialize('json', [plan]))[0]
                success["data"] = serialized_plan
                return JsonResponse(success)
            else:
                # update plan
                plan.hod_approved = True
                plan.date_hod_approved = datetime.now()
                plan.save()
                # save action
                action = PlanAction(action="HOD Approved", plan=plan, member=user.profile.member)
                action.save()
                # make json return
                serialized_plan = json.loads(serialize('json', [plan]))[0]
                success["data"] = serialized_plan
                return JsonResponse(success)
        else:
            return JsonResponse(error)


@login_required
def submit_plan(request):
    if request.method == "POST":
        password = request.POST["password"]
        user = get_user(request)
        department = user.profile.member.user_department
        hod_unapproved_plans = department.hod_unapproved_plans()
        if len(hod_unapproved_plans):
            messages.warning(request, f"Failed! {len(hod_unapproved_plans)} Plans Not Approved.")
            return redirect("plan:plan")
        user = authenticate(username=user.email, password=password)
        if user:
            department.plan_submitted = True
            department.plan_submitted_date = datetime.now()
            department.save()
            messages.success(request, "Plan Submitted to PDU")
        else:
            messages.warning(request, "Invalid Password!")
    return redirect("plan:plan")


# HEAD OF PDU
@login_required
def department_plans(request, id):
    user = get_user(request)
    entity = user.profile.member.user_department.sub_programme.programme.entity
    departments = get_entity_departments(entity)
    current_department = UserDepartment.objects.get(id=id)
    plans = Plan.objects.filter(user_department_id=id)
    context = {
        "departments": departments,
        "current_department": current_department,
        "plans": plans
    }
    return render(request, 'user_department/entity-plans.html', context)


# AJAX
@login_required
def pdu_approve_plan(request, id):
    success = {
        "message": "SUCCESS",
        "data": None
    }
    error = {
        "message": "ERROR",
        "data": None
    }
    user = get_user(request)
    if request.method == "GET":
        plan = Plan.objects.get(id=id)
        if plan.pdu_approved:
            # update plan
            plan.pdu_approved = False
            plan.date_pdu_approved = None
            plan.consolidation_group = null
            plan.save()
            # save action
            action = PlanAction(action="PDU Unapprove", plan=plan, member=user.profile.member)
            action.save()
            # make json return
            serialized_plan = json.loads(serialize('json', [plan]))[0]
            success["data"] = serialized_plan
            return JsonResponse(success)
        else:
            # update plan
            plan.pdu_approved = True
            plan.date_pdu_approved = datetime.now()
            consolidation_group = ConsolidationGroup.objects.get(expense=plan.chart_of_account)
            plan.consolidation_group = consolidation_group
            plan.save()
            # save action
            action = PlanAction(action="PDU Approved", plan=plan, member=user.profile.member)
            action.save()
            # make json return
            serialized_plan = json.loads(serialize('json', [plan]))[0]
            success["data"] = serialized_plan
            return JsonResponse(success)
    else:
        return JsonResponse(error)


@login_required
def receive_department_plan(request, id):
    if request.method == "POST":
        password = request.POST["password"]
        user = get_user(request)
        department = UserDepartment.objects.get(id=id)
        pdu_unapproved_plans = department.pdu_unapproved_plans()
        if len(pdu_unapproved_plans):
            messages.warning(request, f"Failed! {len(pdu_unapproved_plans)} Plans to Approve in '{department}'")
            return redirect("plan:department_plans", id=department.id)
        user = authenticate(username=user.email, password=password)
        if user:
            department.plan_received = True
            department.plan_received_date = datetime.now()
            department.save()
            messages.success(request, f"Received Plan for '{department}'")
        else:
            messages.warning(request, "Invalid Password!")
    return redirect("plan:department_plans", id=department.id)


@login_required
def revert_plan(request, id):
    if request.method == "POST":
        password = request.POST["password"]
        reason = request.POST["password"]
        user = get_user(request)
        department = UserDepartment.objects.get(id=id)
        user = authenticate(username=user.email, password=password)
        if len(department.pdu_unapproved_plans()) == 0:
            messages.warning(request, f"Failed! All Plans have been approved'")
            return redirect("plan:department_plans", id=department.id)
        if user:
            # save reversion
            department.plan_reverted = True
            department.plan_reverted_date = datetime.now()
            department.plan_reverted_reason = reason
            # unsubmit plan
            department.plan_submitted = False
            department.plan_submitted_date = None
            # unprepare plan
            department.plan_prepared = False
            department.plan_prepared_date = None
            department.save()
            messages.info(request, f"Plan Reverted back to '{department}'")
        else:
            messages.warning(request, "Invalid Password!")
    return redirect("plan:department_plans", id=department.id)


@login_required
def plan_consolidation(request):
    user = get_user(request)
    entity = user.profile.member.user_department.sub_programme.programme.entity
    groups = ConsolidationGroup.objects.filter(entity=entity)

    context = {
        "groups" : groups
    }

    return render(request, "user_department/consolidation.html", context)


@login_required
def edit_consolidation_group(request, id):
    if request.method == 'POST':
        subject_of_procurement = request.POST['subject_of_procurement']
        contract_type = request.POST['contract_type']
        prequalification = request.POST.get('prequalification')
        bid_invitation_date = request.POST['bid_invitation_date']
        bid_opening_date = request.POST['bid_opening_date']
        approval_of_bid_evaluation_date = request.POST['approval_of_bid_evaluation_date']
        award_notification_date = request.POST['award_notification_date']
        contract_signing_date = request.POST['contract_signing_date']
        contract_completion_date = request.POST['contract_completion_date']

        group = ConsolidationGroup.objects.get(id=id)
        group.subject_of_procurement = subject_of_procurement
        group.contract_type = contract_type
        if prequalification: group.prequalification = True
        else: group.prequalification = False
        if bid_invitation_date: group.bid_invitation_date = bid_invitation_date
        if bid_opening_date: group.bid_closing_date = bid_opening_date
        if approval_of_bid_evaluation_date: group.bid_approval_and_evaluation_date = approval_of_bid_evaluation_date
        if award_notification_date: group.award_notification_date = award_notification_date
        if contract_signing_date: group.contract_signing_date = contract_signing_date
        if contract_completion_date: group.contract_completion_date = contract_completion_date
        group.save()

    return redirect('plan:plan_consolidation')
