from django import forms

from .models import Order


class CheckoutForm(forms.Form):
    location = forms.CharField(max_length=200)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    payment_method = forms.ChoiceField(choices=Order.PaymentMethod.choices)


class CustomerSignupForm(forms.Form):
    name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=20)
    pin = forms.CharField(max_length=4, min_length=4, widget=forms.PasswordInput)
    confirm_pin = forms.CharField(max_length=4, min_length=4, widget=forms.PasswordInput)

    def clean_phone(self):
        phone = "".join(ch for ch in self.cleaned_data["phone"] if ch.isdigit() or ch == "+")
        if len(phone) < 9:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

    def clean_pin(self):
        pin = self.cleaned_data["pin"]
        if not pin.isdigit():
            raise forms.ValidationError("PIN must be exactly 4 digits.")
        return pin

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("pin") and cleaned.get("confirm_pin") and cleaned["pin"] != cleaned["confirm_pin"]:
            self.add_error("confirm_pin", "PINs do not match.")
        return cleaned


class CustomerLoginForm(forms.Form):
    phone = forms.CharField(max_length=20)
    pin = forms.CharField(max_length=4, min_length=4, widget=forms.PasswordInput)

    def clean_phone(self):
        phone = "".join(ch for ch in self.cleaned_data["phone"] if ch.isdigit() or ch == "+")
        if len(phone) < 9:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone
