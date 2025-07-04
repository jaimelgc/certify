import os
import tempfile
import uuid
from django.shortcuts import render
from django.http import FileResponse, HttpResponseBadRequest
from .forms import UploadForm
from .pdf_utils import clean_pdf, sign_single_pdf
from django.conf import settings

def upload_and_sign(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            if not uploaded_file.name.endswith('.pdf'):
                return HttpResponseBadRequest("Only PDF files are supported.")

            # Create temporary files
            try:
                with tempfile.NamedTemporaryFile(suffix="_original.pdf", delete=False) as original_temp, \
                     tempfile.NamedTemporaryFile(suffix="_cleaned.pdf", delete=False) as cleaned_temp, \
                     tempfile.NamedTemporaryFile(suffix="_signed.pdf", delete=False) as signed_temp:

                    # Save uploaded file
                    for chunk in uploaded_file.chunks():
                        original_temp.write(chunk)

                    original_path = original_temp.name
                    cleaned_path = cleaned_temp.name
                    signed_path = signed_temp.name

                # Clean the PDF
                clean_pdf(original_path, cleaned_path)

                # Sign the PDF
                sign_single_pdf(
                    input_path=cleaned_path,
                    output_path=signed_path,
                    pfx_path=settings.PFX_PATH,
                    pfx_password=settings.PFX_PASSWORD
                )

                # Return signed file
                response = FileResponse(
                    open(signed_path, 'rb'),
                    as_attachment=True,
                    filename='signed_document.pdf'
                )

                # Clean up temp files after 3 seconds
                import threading
                threading.Timer(3, lambda: [os.remove(p) for p in (original_path, cleaned_path, signed_path)]).start()

                return response

            except Exception as e:
                return HttpResponseBadRequest(f"Error signing PDF: {e}")

    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form})
