from django import forms

sources_of_funding = [("GOU", "GOU"), ("Project Funding", "Project Funding")]


class PlanItemForm(forms.Form):
    chart_of_account = forms.ChoiceField()
    subject_of_procurement = forms.CharField(initial="Rent (Produced Assets) to private entities")
    type_of_procurement = forms.ChoiceField()
    quantity = forms.IntegerField(initial=4)
    unit = forms.CharField(initial='Months')
    estimated_cost = forms.IntegerField(initial=5000000)
    source_of_funding = forms.CharField(widget=forms.RadioSelect(choices=sources_of_funding))
    date_required_q1 = forms.BooleanField(required=False)
    date_required_q2 = forms.BooleanField(required=False)
    date_required_q3 = forms.BooleanField(required=False)
    date_required_q4 = forms.BooleanField(required=False)


class PlanConsolidationForm(forms.Form):
    prequalification = forms.BooleanField()
    bid_invitation_date = forms.DateField()
    bid_closing_date = forms.DateField()
    approval_of_evaluation_date = forms.DateField()
    contract_signing_date = forms.DateField()
    contract_completion_date = forms.DateField()