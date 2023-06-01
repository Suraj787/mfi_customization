import frappe
from frappe import _
import os
import subprocess
import shutil
from PIL import Image


def compress_files(doc, method):
    compressed_file_extensions = ['.pdf', '.docx', '.xlsx']
    if os.path.splitext(doc.file_name)[1].lower() in compressed_file_extensions:
        frappe.log_error(title=f'B4 compression {doc.file_name} ', message=f'{doc.file_size}')
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

        os.rename(downsized_file_path, file_path)

        doc.file_url = doc.file_url.rstrip(".downsized")
        doc.file_name = doc.file_name.rstrip(".downsized")
        frappe.log_error(title=f'After compression {doc.file_name} ', message=f'{doc.file_size}')

def file_after_insert(doc, method):
    compress_image(doc)
    # compress_gif(doc)


def file_after_update(doc, method):
    compress_image(doc)
    # compress_gif(doc)



def compress_image(doc):
    frappe.log_error(f'B4 compression {doc.file_name}: {doc.file_size}')
    if os.path.splitext(doc.file_name)[1].lower() in ['.jpeg', '.jpg', '.png']:
        # Path to the uploaded image file
        image_path = os.path.join(frappe.get_site_path(), doc.file_url[1:])

        # Open the image using Pillow
        with Image.open(image_path) as image:
            # Compress the image with desired settings (e.g., reducing the quality)
            compressed_image = image.copy()
            compressed_image.save(image_path, optimize=True, quality=30)

            # Update the file size of the compressed image
            doc.file_size = os.path.getsize(image_path)
            frappe.log_error(f'After compression {doc.file_name}: {doc.file_size}')

            # Update the file record in the database
            doc.save()


def compress_gif(doc):
    print('*************compress_gif***************')
    # Specify the maximum file size for compression in bytes
    max_file_size = 1024 * 1024  # 1MB
    print('****************b4 doc.file_size****************', doc.file_size)
    # Check if the uploaded file is a GIF and exceeds the maximum file size for compression
    if os.path.splitext(doc.file_name)[1].lower() == '.gif' and doc.file_size > max_file_size:
        # Path to the uploaded GIF file
        gif_path = os.path.join(frappe.get_site_path(), doc.file_url[1:])

        # Open the GIF using Pillow
        with Image.open(gif_path) as gif:
            # Reduce the frame size by half
            width, height = gif.size
            gif_resized = gif.resize((width // 1, height // 1), Image.Resampling.LANCZOS)

            # Adjust the color palette to reduce the number of colors
            gif_compressed = gif_resized.quantize(method=Image.Quantize.MEDIANCUT)

            # Save the compressed GIF with improved quality settings
            save_params = {
                'optimize': True,
                'save_all': True,
                'append_images': [gif_compressed],
                'duration': gif.info.get('duration'),
                'loop': gif.info.get('loop'),
                'transparency': gif.info.get('transparency'),
            }
            if 'disposal' in gif.info:
                save_params['disposal'] = gif.info['disposal']

            gif_compressed.save(gif_path, **save_params)

            # Update the file size of the compressed GIF
            doc.file_size = os.path.getsize(gif_path)
            print('****************after doc.file_size****************', doc.file_size)
            # Update the file record in the database
            doc.save()