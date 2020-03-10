from django.urls import path
from plan.views import views, system_views, role_views


app_name = "plan"

urlpatterns = [
    path('', system_views.index, name='index'),
    path('login', system_views.login_view, name='login'),
    path('logout', system_views.logout_view, name='logout'),

    path('plan', views.plan, name='plan'),
    path('add-plan', views.add_plan, name='add_plan'),
    path('edit-plan/<int:id>', views.edit_plan, name='edit_plan'),
    path('remove-plan', views.remove_plan, name='remove_plan'),
    path('finish-plan-preparation', views.finish_plan_preparation, name='finish_plan_preparation'),

    path('comment/<int:id>', views.comment, name='comment'),
    path('plan-details/<int:id>', views.plan_details, name='plan_details'),

    path('hod-approve-plan/<int:id>', views.hod_approve_plan, name='hod_approve_plan'),  # AJAX
    path('submit-plan', views.submit_plan, name='submit_plan'),

    path('entity-plans/<int:id>', views.department_plans, name='department_plans'),
    path('receive-department-plan/<int:id>', views.receive_department_plan, name='receive_department_plan'),
    path('pdu-approve-plan/<int:id>', views.pdu_approve_plan, name='pdu_approve_plan'),  # AJAX
    path('revert-plan/<int:id>', views.revert_plan, name='revert_plan'),

    path('plan-consolidation', views.plan_consolidation, name='plan_consolidation'),

    path('roles', role_views.roles, name='roles'),
    path('assign-reparation-role/', role_views.assign_preparation_role, name='assign_preparation_role'),
]