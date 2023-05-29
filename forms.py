from django import forms
from . models import Common, Subscription, FreeSubscription

class ContractForm(forms.ModelForm):

    payment_type = forms.TypedChoiceField(choices=Common.PAYMENT_TYPES, 
        initial=Common.PAYMENT_TYPES[4][0], required=True)
    class Meta:
        model = Contract
        fields = [
            'payment_type',
            'subscription',
            'state',
            'last_date',
            'client_tier',
            'client',
            'user',
            'description',
        ]

class CommonForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
        self.fields['amount'].required = True
        if kwargs['initial'].get('order') >=0:
            self.fields.get('content').widget.attrs['class'] = "parts-{}-content".format(kwargs['initial'].get('order'))
            self.fields.get('content').widget.attrs['id'] = "id_parts-{}-content".format(kwargs['initial'].get('order'))
    class Meta:
        model = Common
        fields = [
            'order',
            'title',
            'title_tooltip',
            'content',
            'template_file',
            'amount',
        ]
