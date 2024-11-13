import docx
import magic

from io import BytesIO
from PyPDF2 import PdfReader
import pymupdf

def read_file_content(file: BytesIO):
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file.getvalue())

    extracted_text = None
    if 'pdf' in file_type.lower():
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        extracted_text = text.strip() or "<Could not extract text from the PDF>"
    elif 'officedocument' in file_type.lower() or 'msword' in file_type.lower():
        doc = docx.Document(file)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        extracted_text = text.strip() or "<Could not extract text from the DOCX file>"

    return extracted_text, file_type

def pdf_to_png(file: BytesIO, max_height=2048, max_width=2048):
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file.getvalue())
    file_bytes = file.getvalue()

    result = []

    if 'pdf' in file_type.lower():
        pdf = pymupdf.open(stream=file_bytes, filetype="pdf")
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            rect = page.rect
            scale = min(max_width/rect.width, max_height/rect.height)
            matrix = pymupdf.Matrix(scale, scale)
            pixmap = page.get_pixmap(matrix=matrix)
            img = pixmap.tobytes("png")
            result.append(BytesIO(img))
        pdf.close()
    return result
