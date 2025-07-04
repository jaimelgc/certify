from django import forms

class UploadForm(forms.Form):
    file = forms.FileField()
    pfx_file = forms.FileField()
