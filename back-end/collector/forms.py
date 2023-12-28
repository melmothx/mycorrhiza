from django import forms
class SpreadsheetForm(forms.Form):
    error_css_class = "error"
    required_css_class = "required"
    comments = forms.CharField(label="Comments", max_length=200)
    sheet = forms.FileField()
