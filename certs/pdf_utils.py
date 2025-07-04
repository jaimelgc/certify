import pikepdf
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.writer import copy_into_new_writer
from pyhanko.sign.fields import SigFieldSpec, append_signature_field
from pyhanko.sign.signers import SimpleSigner, PdfSigner
from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata

def clean_pdf(input_path, output_path):
    """Sanitize a PDF to ensure it's valid and compatible for signing."""
    try:
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path, linearize=True)
    except pikepdf.PdfError as e:
        raise ValueError(f"Failed to clean PDF: {e}")


def sign_single_pdf(input_path, output_path, pfx_path, pfx_password):
    # Try loading the signer
    try:
        signer = SimpleSigner.load_pkcs12(
            pfx_file=pfx_path,
            passphrase=pfx_password.encode('utf-8'),
        )
        if signer is None:
            raise ValueError("Signer is None — possibly invalid .pfx or wrong password")
        if signer.signing_cert is None or signer.signing_key is None:
            raise ValueError("Signer is missing cert or key — invalid .pfx content")
    except Exception as e:
        raise ValueError(f"Failed to load signer: {e}")

    # Continue signing
    with open(input_path, 'rb') as inf:
        reader = PdfFileReader(inf)
        total_pages = len(reader.root['/Pages']['/Kids'])

        # Signature box settings
        signature_box = (400, 50, 550, 100)
        target_page = total_pages - 1

        sig_field = SigFieldSpec(
            sig_field_name="Signature1",
            box=signature_box,
            on_page=target_page
        )

        writer = copy_into_new_writer(reader)
        append_signature_field(writer, sig_field)

        with open(output_path, 'wb') as outf:
            pdf_signer = PdfSigner(
                signature_meta=PdfSignatureMetadata(
                    field_name=sig_field.sig_field_name,
                    reason="Firma electrónica",
                    location="Web App"
                ),
                signer=signer
            )
            pdf_signer.sign_pdf(writer, output=outf)

