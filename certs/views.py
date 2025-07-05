import os
import tempfile
import uuid
from django.shortcuts import render
from django.http import FileResponse, HttpResponseBadRequest
from .forms import UploadForm
from .pdf_utils import clean_pdf, sign_single_pdf

def upload_and_sign(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            pfx_file = request.FILES['pfx_file']
            pfx_password = form.cleaned_data['pfx_password']
            position = form.cleaned_data['position']
            page = form.cleaned_data['page']

            if not uploaded_file.name.endswith('.pdf'):
                return HttpResponseBadRequest("Only PDF files are supported.")

            # Create temporary files
            original_path = None
            cleaned_path = None
            signed_path = None
            pfx_path = None
            
            try:
                # Create temporary files
                with tempfile.NamedTemporaryFile(suffix="_original.pdf", delete=False) as original_temp:
                    for chunk in uploaded_file.chunks():
                        original_temp.write(chunk)
                    original_path = original_temp.name

                with tempfile.NamedTemporaryFile(suffix="_cleaned.pdf", delete=False) as cleaned_temp:
                    cleaned_path = cleaned_temp.name

                with tempfile.NamedTemporaryFile(suffix="_signed.pdf", delete=False) as signed_temp:
                    signed_path = signed_temp.name

                # Save PFX file temporarily
                with tempfile.NamedTemporaryFile(suffix=".pfx", delete=False) as pfx_temp:
                    for chunk in pfx_file.chunks():
                        pfx_temp.write(chunk)
                    pfx_path = pfx_temp.name

                # Clean the PDF
                clean_pdf(original_path, cleaned_path)

                # Sign the PDF with user parameters
                sign_single_pdf(
                    input_path=cleaned_path,
                    output_path=signed_path,
                    pfx_path=pfx_path,
                    pfx_password=pfx_password,
                    position=position,
                    page=page
                )

                # Return signed file
                response = FileResponse(
                    open(signed_path, 'rb'),
                    as_attachment=True,
                    filename='signed_document.pdf'
                )

                # Clean up temp files after response
                import threading
                def cleanup():
                    for path in [original_path, cleaned_path, signed_path, pfx_path]:
                        if path and os.path.exists(path):
                            try:
                                os.remove(path)
                            except OSError:
                                pass
                
                threading.Timer(3, cleanup).start()

                return response

            except Exception as e:
                # Clean up temp files on error
                for path in [original_path, cleaned_path, signed_path, pfx_path]:
                    if path and os.path.exists(path):
                        try:
                            os.remove(path)
                        except OSError:
                            pass
                
                return HttpResponseBadRequest(f"Error signing PDF: {e}")

    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form})