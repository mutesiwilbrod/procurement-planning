from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# SYSTEM MODELS
class Expense(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=128)

    def __str__(self):
        return " ".join([self.code, "-", self.name])

    def generate_field_choices(self):
        return [(expense.id, expense.name) for expense in self.objects.all()]

    def plans_for_departments(self, departments):
        return Plan.objects.filter(user_department__in=departments, chart_of_account=self)


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

    def __str__(self):
        return " ".join([str(self.code), str(self.name)])

    def programmes(self):
        return Programme.objects.filter(entity=self)


class ConsolidationGroup(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    subject_of_procurement = models.CharField(max_length=128, null=True)
    source_of_funding = models.CharField(max_length=128, null=True)
    contract_type = models.CharField(max_length=64, null=True)
    prequalification = models.BooleanField(null=True)
    bid_invitation_date = models.DateTimeField(null=True)
    bid_closing_date = models.DateTimeField(null=True)
    bid_approval_and_evaluation_date = models.DateTimeField(null=True)
    award_notification_date = models.DateTimeField(null=True)
    contract_signing_date = models.DateTimeField(null=True)
    contract_completion_date = models.DateTimeField(null=True)

    def __str__(self):
        return subject_of_procurement

    def plans(self):
        return Plan.objects.filter(consolidation_group=self)

    def pdu_approved_plans_for_departments(self, departments):
        return Plan.objects.filter(user_department__in=departments, chart_of_account=self, pdu_approved=True)

    def method_of_procurement(self):
        plan_cost = self.total_estimated_cost()
        if plan_cost < 1000000:
            return 'Micro Procurement'
        elif plan_cost < 10000000:
            return 'RFQ'
        else:
            return 'International Bidding'
            

class Programme(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    def __str__(self):
        return " ".join([self.code, "-", self.name])

    def sub_programmes(self):
        return SubProgramme.objects.filter(programme=self)


class SubProgramme(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)

    def __str__(self):
        return " ".join([self.code, "-", self.name])

    def user_departments(self):
        return UserDepartment.objects.filter(sub_programme=self)


class AccountingOfficer(models.Model):
    requisition_approval = models.BooleanField(default=True)
    plan_approval = models.BooleanField(default=True)


class HeadOfPDU(models.Model):
    plan_approval = models.BooleanField(default=True)
    role_deligation = models.BooleanField(default=True)


class PDUMember(models.Model):
    plan_consolidation = models.BooleanField(default=False)


class VoteController(models.Model):
    sub_programme = models.ForeignKey(SubProgramme, on_delete=models.CASCADE)
    requisition_approval = models.BooleanField(default=True)


class HeadOfDepartment(models.Model):
    plan_approval = models.BooleanField(default=True)
    role_deligation = models.BooleanField(default=True)


class DepartmentMember(models.Model):
    plan_preparation = models.BooleanField(default=False)
    requisition_initiation = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User, unique=False, on_delete=models.CASCADE)
    accounting_officer = models.OneToOneField(AccountingOfficer, on_delete=models.CASCADE, null=True)
    head_of_pdu = models.OneToOneField(HeadOfPDU, on_delete=models.CASCADE, null=True)
    pdu_member = models.OneToOneField(PDUMember, on_delete=models.CASCADE, null=True)
    vote_controller = models.OneToOneField(VoteController, on_delete=models.CASCADE, null=True)
    head_of_department = models.OneToOneField(HeadOfDepartment, on_delete=models.CASCADE, null=True)
    department_member = models.OneToOneField(DepartmentMember, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.user)

    # @receiver(post_save, sender=User)
    # def create_user_profile(sender, instance, created, **kwargs):
    #     if created:
    #         Profile.objects.create(user=instance)
    #
    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.profile.save()


class UserDepartment(models.Model):
    name = models.CharField(max_length=100)
    budget_sealing = models.IntegerField()
    plan_prepared = models.BooleanField(default=False)
    plan_prepared_date = models.DateTimeField(null=True)
    plan_submitted = models.BooleanField(default=False)
    plan_submitted_date = models.DateTimeField(null=True)
    plan_received = models.BooleanField(default=False)
    plan_received_date = models.DateTimeField(null=True)
    plan_reverted = models.BooleanField(default=False)
    plan_reverted_date = models.DateTimeField(null=True)
    plan_reverted_reason = models.CharField(null=True)
    plan_reverted_reason = models.CharField(max_length=512, null=True)
    sub_programme = models.ForeignKey(SubProgramme, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_members(self):
        return Member.objects.filter(user_department=self, hod=False)

    def hod(self):
        return Member.objects.get(user_department=self, hod=True)

    def hod_approved_plans(self):
        return Plan.objects.filter(user_department=self, hod_approved=True)

    def hod_unapproved_plans(self):
        return Plan.objects.filter(user_department=self, hod_approved=False)

    def pdu_approved_plans(self):
        return Plan.objects.filter(user_department=self, pdu_approved=True)

    def pdu_unapproved_plans(self):
        return Plan.objects.filter(user_department=self, pdu_approved=False)

    def plans(self):
        return Plan.objects.filter(user_department=self)

    def total_amount_planned(self):
        plans = Plan.objects.filter(user_department=self)
        return sum([plan.estimated_cost for plan in plans])

    def get_plan_preparation_member(self):
        for member in self.get_members():
            if member.profile.department_member.plan_preparation:
                return member
        return None


class Member(models.Model):
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    title = models.CharField(max_length=30, default="")
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    hod = models.BooleanField(default=False)
    user_department = models.ForeignKey(UserDepartment, on_delete=models.CASCADE)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return " ".join([self.first_name, self.last_name])


class Plan(models.Model):
    user_department = models.ForeignKey(UserDepartment, on_delete=models.CASCADE)
    chart_of_account = models.ForeignKey(Expense, on_delete=models.CASCADE)
    subject_of_procurement = models.CharField(max_length=100)
    type_of_procurement = models.ForeignKey(ProcurementType, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_of_measure = models.CharField(max_length=100)
    estimated_cost = models.IntegerField()
    source_of_funding = models.CharField(max_length=100) # TODO => split to GOU and Project
    date_required_q1 = models.BooleanField()
    date_required_q2 = models.BooleanField()
    date_required_q3 = models.BooleanField()
    date_required_q4 = models.BooleanField()
    prepared = models.BooleanField(default=True)
    hod_approved = models.BooleanField(default=False)
    pdu_approved = models.BooleanField(default=False)
    reverted = models.BooleanField(default=False)
    consolidated = models.BooleanField(default=False)
    date_prepared = models.DateTimeField(null=True)
    date_hod_approved = models.DateTimeField(null=True)
    date_pdu_approved = models.DateTimeField(null=True)
    date_reverted = models.DateTimeField(null=True)
    date_consolidated = models.DateTimeField(null=True)
    consolidation_group = models.ForeignKey(ConsolidationGroup, on_delete=models.CASCADE, null=True)

    def status(self):
        if self.consolidated:
            return "CONSOLIDATED"
        elif self.reverted:
            return "REVERTED"
        elif self.pdu_approved:
            return "APPROVED (PDU)"
        elif self.hod_approved:
            return "APPROVED (HOD)"
        elif self.prepared:
            return "PREPARED"

    def comments(self):
        return PlanComment.objects.filter(plan=self).order_by("-date")

    def actions(self):
        return PlanAction.objects.filter(plan=self).order_by("-date")


class PlanAction(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=64)
    detail = models.CharField(max_length=512, null=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return self.action


class PlanComment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=512)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return self.action


def setup_plan_app():
    import os
    # os.system('rm -rf plan/migrations; mkdir plan/migrations; touch plan/migrations/__init__.py; rm db.sqlite3; python3 manage.py makemigrations; python3 manage.py migrate;')
    os.system('rmdir /s /q plan\migrations& mkdir plan\migrations')
    file = open('plan/migrations/__init__.py', 'w')
    file.close()
    os.system('del db.sqlite3& python manage.py makemigrations plan& python manage.py migrate')
    # CREATE SUPER USER
    # User.objects.create_superuser('admin', 'admin@example.com', '123')

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
    expenses = []
    for item in items:
        item = Expense(code=item['code'], name=item['name'])
        item.save()
        expenses.append(item)

    # 2. procurement types
    procurement_types = ["Supplies", "Works", "Non-consultancy Services", "Consultancy Services"]
    for _type in procurement_types:
        pt = ProcurementType(name=_type)
        pt.save()

    # LOAD ENTITY DATA
    # 1. entity
    muni_entity = Entity(code="MU127", name="Muni University"); muni_entity.save()

    for expense in expenses:
        group = ConsolidationGroup(subject_of_procurement=expense.name, entity=muni_entity, expense=expense)
        group.save()

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

    # 8. user departments
    departments = [("Office of Accounting Officer", sp2, 10000000),
                   ("Estates", sp2, 100000000),
                   ("Procurement and Disposal", sp2, 10000000),
                   ("Internal Audit", sp2, 30000000),
                   ("Office of the Vice Chancellor", sp2, 30000000),
                   ("Guild", sp3, 30000000),
                   ("Academic Registrar", sp3, 30000000),
                   ("Library", sp2, 40000000),
                   ("Faculty of Education", sp6, 50000000)
                   ]
    departments_objects = []
    for name, sp, sealing in departments:
        ud = UserDepartment(name=name, sub_programme=sp, budget_sealing=sealing)
        ud.save()
        departments_objects.append(ud)

    # 4. accounting officer
    ao = Member(first_name="Rev. Fr. Dr. Picho", last_name="Epiphany Odubuker", title="Univeristy Secretary", email="ao@muni.ac.ug", telephone='256789542563', hod=True, user_department=departments_objects[0])
    ao.save()

    # 5. head of pdu
    pdu_head = Member(first_name="Mr. Anguyo", last_name="Richard", title="Senior Procurement Officer", email="pdu1@muni.ac.ug", telephone='256789542563', hod=True, user_department=departments_objects[2])
    pdu_head.save()

    # 6. pdu members
    pdu1 = Member(first_name="Mr. Nyeko", last_name="Francis", title="Junior Procurement Officer", email="pdu2@muni.ac.ug", telephone='256789542563', user_department=departments_objects[2])
    pdu1.save()
    pdu2 = Member(first_name="Mr. Mutesi", last_name="Wilbrod", title="Asst. Procurement Officer", email="pdu3@muni.ac.ug", telephone='256789542563', user_department=departments_objects[2])
    pdu2.save()

    # 7. Other Members
    m1 = Member(first_name="Mr. Aluonzi", last_name="Godfrey", title="Head of Estates", email="estates1@muni.ac.ug", telephone='256789542563', hod=True, user_department=departments_objects[1]); m1.save()
    m2 = Member(first_name="Prof. Christine", last_name="Dranzoa", title="Vice Chancellor", email="vicechancellor1@muni.ac.ug", telephone='256789542563', hod=True, user_department=departments_objects[4]); m2.save()
    m3 = Member(first_name="Mr. Jesse", last_name="Mugabi", title="Guild President", email="guild1@muni.ac.ug", telephone='256789542563', hod=True, user_department=departments_objects[5]); m3.save();
    m4 = Member(first_name="Mr. Omara", last_name="Polycarp", title="Head of Faculty of Education", email="educ1@muni.ac.ug", telephone='256789542563', hod=True, user_department=departments_objects[8]); m4.save();
    m5 = Member(first_name="Mrs. Small", last_name="Vicky", title="Department Member", email="educ2@muni.ac.ug", telephone='256789542563', user_department=departments_objects[8]); m5.save();
    m6 = Member(first_name="Mrs. Patricia", last_name="Anna", title="Secretary", email="educ3@muni.ac.ug", telephone='256789542563', user_department=departments_objects[8]); m6.save();

    # 8. generate user profiles
    members = [(ao, ['ao', 'mem']), (pdu_head, ['mem', 'pdu_mem', 'pdu_head']),
               (pdu1, ['mem', 'pdu_mem']), (pdu2, ['mem', 'pdu_mem']), (m1, ['mem', 'hod']), (m2, ['mem', 'hod']), (m3, ['mem', 'hod']),
               (m4, ['mem', 'hod']), (m5, ['mem']), (m6, ['mem'])]

    for member, profiles in members:
        user = User.objects.create_user(member.email, member.email, '123')
        user.save()
        prof = Profile(user=user)
        if 'ao' in profiles:
            ao = AccountingOfficer()
            ao.save()
            prof.accounting_officer = ao
        if 'mem' in profiles:
            mem = DepartmentMember()
            mem.save()
            prof.department_member = mem
        if 'pdu_mem' in profiles:
            pdu_mem = PDUMember()
            pdu_mem.save()
            prof.pdu_member = pdu_mem
        if 'pdu_head' in profiles:
            pdu_head = HeadOfPDU()
            pdu_head.save()
            prof.head_of_pdu = pdu_head
        if 'hod' in profiles:
            hod = HeadOfDepartment()
            hod.save()
            prof.head_of_department = hod
        user.profile = prof
        prof.save()
        member.profile = prof
        member.save()