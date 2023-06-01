import frappe
from frappe import _
import os
import subprocess
import shutil
from PIL import Image


def compress_uploaded_file(doc, method):
    compressed_file_extensions = ['.pdf', '.docx', '.xlsx']
    if os.path.splitext(doc.file_name)[1].lower() in compressed_file_extensions:
        frappe.log_error(title=f'Size of {doc.file_name} b4 compressing', message=f'{doc.file_size}')
        file_path = os.path.join(frappe.get_site_path(), doc.file_url[1:])   # Path to the uploaded file
        downsized_file_path = f"{file_path}.downsized"  # Path for the downsized file

        if os.path.splitext(doc.file_name)[1].lower() == '.pdf':
            subprocess.run(["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-sOutputFile={downsized_file_path}", file_path])
        elif os.path.splitext(doc.file_name)[1].lower() in ['.docx', '.xlsx']:
            subprocess.run(["zip", "-j", downsized_file_path, file_path])
        else:
            downsized_file_path = file_path

        doc.file_url = f"/files/{os.path.basename(downsized_file_path)}"
        if doc.is_private:
            doc.file_url = f"/private{doc.file_url}"
        doc.file_name = os.path.basename(downsized_file_path)
        doc.file_size = os.path.getsize(downsized_file_path)

        os.remove(file_path)
        os.rename(downsized_file_path, file_path)

        doc.file_url = doc.file_url.rstrip(".downsized")
        doc.file_name = doc.file_name.rstrip(".downsized")
        frappe.log_error(title=f'Size of {doc.file_name} after compressing', message=f'{doc.file_size}')

