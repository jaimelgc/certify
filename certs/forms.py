from django import forms

POSITIONS = [
    ('(50, 750, 200, 800)', 'Izquierda Superior'),
    ('(400, 750, 550, 800)', 'Derecha Superior'),
    ('(50, 50, 200, 100)', 'Izquierda Inferior'),
    ('(400, 50, 550, 100)', 'Derecha Inferior'),
    ('(222, 396, 372, 446)', 'Centrado'),
]

PAGES = [
    ('ultima', 'Última Página'),
    ('0', 'Primera Página'),
]


class UploadForm(forms.Form):
    file = forms.FileField(label="PDF a firmar")
    pfx_file = forms.FileField(label="Archivo PFX")
    pfx_password = forms.CharField(
        widget=forms.PasswordInput, label="Contraseña del archivo PFX", max_length=100
    )
    position = forms.ChoiceField(
        choices=POSITIONS, widget=forms.RadioSelect, label="Posición de la firma"
    )
    page = forms.ChoiceField(choices=PAGES, widget=forms.RadioSelect, label="Página a firmar")

    def clean_pfx_file(self):
        pfx_file = self.cleaned_data.get('pfx_file')
        if pfx_file:
            if not pfx_file.name.lower().endswith('.pfx'):
                raise forms.ValidationError("El archivo debe tener extensión .pfx")
        return pfx_file
