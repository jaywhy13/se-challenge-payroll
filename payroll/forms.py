from django import forms


class TimesheetUploadForm(forms.Form):

    timesheet = forms.FileField()
