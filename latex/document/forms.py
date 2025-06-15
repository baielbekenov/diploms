from django import forms


class ContractGenerationForm(forms.Form):
    client_name = forms.CharField(max_length=255)
    service_description = forms.CharField(widget=forms.Textarea)
    total_price = forms.DecimalField(max_digits=10, decimal_places=2)