from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# SYSTEM MODELS
class Expense(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return " ".join([self.code, "-", self.name])

    def generate_field_choices(self):
        return [(expense.id, expense.name) for expense in self.objects.all()]


class ProcurementType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def generate_field_choices(self):
        return [(_type.id, _type.name) for _type in self.objects.all()]


# ENTITY MODELS
class Entity(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=100)
    AO_first_name = models.CharField(max_length=64)
    AO_last_name = models.CharField(max_length=64)
    AO_title = models.CharField(max_length=64)
    AO_username = models.CharField(max_length=64)
    telephone = models.CharField(max_length=15)
    email = models.CharField(max_length=64)

    def __str__(self):
        return " ".join([str(self.code), str(self.name)])


class Programme(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def __str__(self):
        return " ".join([self.code, "-", self.name])


class SubProgramme(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)

    def __str__(self):
        return " ".join([self.code, "-", self.name])


class AccountingOfficer(models.Model):
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    title = models.CharField(max_length=30)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def __str__(self):
        return " ".join([str(self.first_name), str(self.last_name)])


class PDUMember(models.Model):
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    title = models.CharField(max_length=30)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    head = models.BooleanField(default=False)

    def __str__(self):
        return " ".join([str(self.first_name), str(self.last_name)])


class UserDepartment(models.Model):
    department_name = models.CharField(max_length=100)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name

    def get_members(self):
        return Member.objects.filter(user_department=self)


class VoteController(models.Model):
    sub_programme = models.ForeignKey(SubProgramme, on_delete=models.CASCADE)


class Member(models.Model):
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    title = models.CharField(max_length=30, default="")
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    user_department = models.ForeignKey(UserDepartment, on_delete=models.CASCADE)
    vote_controller = models.ForeignKey(VoteController, on_delete=models.CASCADE, null=True)
    plan_preparation_role = models.BooleanField(null=True)
    plan_approval_role = models.BooleanField(null=True)
    requisition_initiation_role = models.BooleanField(null=True)

    def __str__(self):
        return " ".join([str(self.first_name), str(self.last_name)])

    def get_plan_preparer(self):
        return Member.objects.get(plan_preparation_role=True)

    def get_plan_approver(self):
        return Member.objects.get(plan_approval_role=True)


class Profile(models.Model):
    user = models.OneToOneField(User, unique=False, on_delete=models.CASCADE)
    accounting_officer = models.OneToOneField(AccountingOfficer, on_delete=models.CASCADE, null=True)
    vote_controller = models.OneToOneField(VoteController, on_delete=models.CASCADE, null=True)
    pdu_member = models.OneToOneField(PDUMember, on_delete=models.CASCADE, null=True)
    member = models.OneToOneField(Member, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.user)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class PlanStatus(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=512, null=True)

    def __str__(self):
        return self.name


class Plan(models.Model):
    user_department = models.ForeignKey(UserDepartment, on_delete=models.CASCADE)
    prepared_by = models.ForeignKey(Member, related_name="preparer", on_delete=models.CASCADE, null=True)
    approved_by = models.ForeignKey(Member, related_name="approver", on_delete=models.CASCADE, null=True)
    start_date_of_preparation = models.DateTimeField(auto_now_add=True)
    stop_date_of_preparation = models.DateTimeField(null=True)
    date_of_approval = models.DateTimeField(null=True)

    def get_plan_items(self):
        return PlanItem.objects.filter(plan=self)


class PlanItem(models.Model):
    chart_of_account = models.ForeignKey(Expense, on_delete=models.CASCADE)
    subject_of_procurement = models.CharField(max_length=100)
    type_of_procurement = models.ForeignKey(ProcurementType, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_of_measure = models.CharField(max_length=100)
    estimated_cost = models.IntegerField()
    source_of_funding = models.CharField(max_length=100)
    date_required_q1 = models.BooleanField()
    date_required_q2 = models.BooleanField()
    date_required_q3 = models.BooleanField()
    date_required_q4 = models.BooleanField()
    added_by = models.ForeignKey(Member, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    status = models.ForeignKey(PlanStatus, on_delete=models.CASCADE)


def setup_plan_app():
    import os
    os.system('rm -rf plan/migrations; mkdir plan/migrations; touch plan/migrations/__init__.py; rm db.sqlite3; python3 manage.py makemigrations; python3 manage.py migrate;')

    # CREATE SUPER USER
    User.objects.create_superuser('admin', 'admin@example.com', '123')

    # LOAD SYSTEM DATA
    # 1. expenses
    items = [
        {"code": 211101, "name":"General Staff Salaries"},
        {"code": 211102, "name": "Contract Staff Salaries and wages"},
        {"code": 211103, "name": "Allowances"}
    ]
    # import json
    # items_file = open('items.json')
    # items = json.loads(items_file.read())

    for item in items:
        item = Expense(code=item['code'], name=item['name'])
        item.save()

    # 2. procurement types
    procurement_types = ["Supplies", "Works", "Non-consultancy Services", "Consultancy Services"]
    for _type in procurement_types:
        pt = ProcurementType(name=_type)
        pt.save()

    # 3. plan statuses
    statuses = [
        {"code": 1, "name": "PREPARED"},
        {"code": 2, "name": "HOD_APPROVED"},
        {"code": 3, "name": "REVERTED"},
        {"code": 4, "name": "CONSOLIDATED"}
    ]
    for status in statuses:
        plan_status = PlanStatus(code=status['code'], name=status['name'])
        plan_status.save()

    # 3. financial years

    # LOAD ENTITY DATA
    # 1. entity
    muni_entity = Entity(code="MU127", name="Muni University", AO_first_name="Rev. Fr. Dr. Picho",
                         AO_last_name="Epiphany Odubuker", AO_title="Univeristy Secretary", email="ao@muni.ac.ug",
                         telephone='256789542563'); muni_entity.save()

    # 2. programs
    p1 = Programme(code="0751", name="Delivery of Tertiary Education and Research", entity=muni_entity); p1.save()
    p2 = Programme(code="0713", name="Support Services Programme", entity=muni_entity); p2.save()
    p3 = Programme(code="0714", name="Delivery of Tertiary Education Programme", entity=muni_entity); p3.save()

    # 3. sub-programs and vote_controllers
    sp1 = SubProgramme(code="01", name="Headquarters", programme=p1); sp1.save()
    vc1 = VoteController(sub_programme=sp1); vc1.save()

    sp2 = SubProgramme(code="02", name="Central Administration", programme=p2); sp2.save()
    vc2 = VoteController(sub_programme=sp2); vc2.save()

    sp3 = SubProgramme(code="03", name="Academic and Student Affairs", programme=p2); sp3.save()
    vc3 = VoteController(sub_programme=sp3); vc3.save()

    sp4 = SubProgramme(code="04", name="Faculty of Technoscience", programme=p3); sp4.save()
    vc4 = VoteController(sub_programme=sp4); vc4.save()

    sp5 = SubProgramme(code="05", name="Research and Innovation Department", programme=p3); sp5.save()
    vc5 = VoteController(sub_programme=sp5); vc5.save()

    sp6 = SubProgramme(code="06", name="Faculty of Education", programme=p3); sp6.save()
    vc6 = VoteController(sub_programme=sp6); vc6.save()

    sp7 = SubProgramme(code="07", name="Faculty of Health Sciences", programme=p3); sp7.save()
    vc7 = VoteController(sub_programme=sp7); vc7.save()

    sp8 = SubProgramme(code="08", name="Faculty of Science", programme=p3); sp8.save()
    vc8 = VoteController(sub_programme=sp8); vc8.save()

    sp9 = SubProgramme(code="09", name="Agriculture and Environmental Science", programme=p3); sp9.save()
    vc9 = VoteController(sub_programme=sp9); vc9.save()

    sp10 = SubProgramme(code="10", name="Faculty of Management Science", programme=p3); sp10.save()
    vc10 = VoteController(sub_programme=sp10); vc10.save()

    # 4. accounting officer
    ao = AccountingOfficer(first_name="Rev. Fr. Dr. Picho", last_name="Epiphany Odubuker",
                           title="Univeristy Secretary", email="ao@muni.ac.ug", telephone='256789542563',
                           entity=muni_entity)
    ao.save()

    # 5. pdu members
    pdu1 = PDUMember(first_name="Mr. Anguyo", last_name="Richard",
                           title="Senior Procurement Officer", email="pdu1@muni.ac.ug", telephone='256789542563',
                           entity=muni_entity)
    pdu1.save()
    pdu2 = PDUMember(first_name="Mr. Nyeko", last_name="Francis",
                     title="Junior Procurement Officer", email="pdu2@muni.ac.ug", telephone='256789542563',
                     entity=muni_entity)
    pdu2.save()
    pdu2 = PDUMember(first_name="Mr. Mutesi", last_name="Wilbrod",
                     title="Asst. Procurement Officer", email="pdu3@muni.ac.ug", telephone='256789542563',
                     entity=muni_entity)
    pdu2.save()

    # 6. user departments
    ud1 = UserDepartment(department_name="Faculty of Technoscience", entity=muni_entity)
    ud1.save()

    # 7. members
    u1 = Member(first_name="Small", last_name="Vicky", title="Secretary", email="s.vicky@muni.ac.ug",
                telephone='256789542563', user_department=ud1)
    u1.save()

    u2 = Member(first_name="Dr Andogah", last_name="Geoffrey", title="Dean of Faculty of Technoscience", email="g.andogah@muni.ac.ug",
                telephone='256789542563', user_department=ud1, vote_controller=vc4, plan_preparation_role=True, plan_approval_role=True)
    u2.save()

    u3 = Member(first_name="Itwaru", last_name="Samuel", title="Lecturer",
                email="s.itwaru@muni.ac.ug", telephone='256789542563', user_department=ud1, vote_controller=vc4)

    u3.save()

    # 8. generate user profiles
    users = [
        {'user': ao, 'role': 'ao'},
        {'user': pdu1, 'role': 'pdu'},
        {'user': pdu2, 'role': 'pdu'},
        {'user': u1, 'role': 'member'},
        {'user': u2, 'role': 'member'},
        {'user': u3, 'role': 'member'},
    ]

    # user = User.objects.create_user(users[0]['user'].email, users[0]['user'].email, '123')
    # user.profile.office_member = ao
    # user.save()

    for each in users:
        user = User.objects.create_user(each['user'].email, each['user'].email, '123')
        if each['role'] == 'pdu':
            user.profile.pdu_member = each['user']
        elif each['role'] == 'vc':
            user.profile.vote_controller = each['user']
        elif each['role'] == 'ao':
            user.profile.accounting_officer = each['user']
        elif each['role'] == 'member':
            user.profile.member = each['user']
        user.save()

    # 10. generate plans
    plan = Plan(user_department=ud1)
    plan.save()