from django.forms import ModelForm
from .models import SpreadsheetUpload
class SpreadsheetForm(ModelForm):
    class Meta:
        error_css_class = "error"
        required_css_class = "required"
        model = SpreadsheetUpload
        fields = [
            "spreadsheet",
            "comment",
            "site",
            "csv_type",
            "replace_all",
        ]
