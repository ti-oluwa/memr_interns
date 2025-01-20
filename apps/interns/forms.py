from django import forms

from .models import Internship


class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = [
            "internship_type",
            "department",
            "start_date",
            "end_date",
            "duration",
        ]

        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                {"end_date": "End date must be greater than start date."}
            )
        return cleaned_data
