import pymupdf
import docx
from io import BytesIO

def read_file_content(file: BytesIO, include_styles=False):
    signature = file.read(4)
    file.seek(0)
    file_bytes = file.getvalue()

    if signature.startswith(b'%PDF'):
        pdf = pymupdf.open(stream=file_bytes, filetype="pdf")
        content = []
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if include_styles:
                                span_info = {
                                    'text': span['text'],
                                    'font': span['font'],
                                    'size': span['size'],
                                    'color': span['color'],
                                    'flags': span['flags']
                                }
                            else:
                                span_info = span["text"]
                            content.append(span_info)
        pdf.close()
        return content
    elif signature == b'PK\x03\x04':
        doc = docx.Document(file)
        content = []
        for paragraph in doc.paragraphs:
            if include_styles:
                para_info = {
                    'text': paragraph.text,
                    'style': paragraph.style.name,
                    'alignment': paragraph.alignment,
                    'runs': []
                }

                for run in paragraph.runs:
                    run_info = {
                        'text': run.text,
                        'bold': run.bold,
                        'italic': run.italic,
                        'underline': run.underline,
                        'font': run.font.name if run.font.name else None,
                        'size': run.font.size.pt if run.font.size else None,
                        'color': f"rgb({run.font.color.rgb[0]},{run.font.color.rgb[1]},{run.font.color.rgb[2]})" if run.font.color and run.font.color.rgb else None
                    }
                    para_info['runs'].append(run_info)
                content.append(para_info)
            else:
                content.append(paragraph.text)
        return content
    else:
        return []

def pdf_to_png(file: BytesIO, max_height=2048, max_width=2048):
    signature = file.read(4)
    file.seek(0)
    file_bytes = file.getvalue()

    result = []

    if signature.startswith(b'%PDF'):
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


if __name__ == "__main__":
    with open("test.pdf", "rb") as f:
        pdf_file = BytesIO(f.read())
        print(pdf_to_png(pdf_file))
        print()

    with open("test.pdf", "rb") as f:
        pdf_file = BytesIO(f.read())
        content = read_file_content(pdf_file)
        print(content)
        print()

    with open("test.pdf", "rb") as f:
        pdf_file = BytesIO(f.read())
        content_styled = read_file_content(pdf_file, include_styles=True)
        print(content_styled)
        print()

    with open("test.docx", "rb") as f:
        docx_file = BytesIO(f.read())
        docx_content = read_file_content(docx_file)
        print(docx_content)
        print()

    with open("test.docx", "rb") as f:
        docx_file = BytesIO(f.read())
        docx_content_styled = read_file_content(docx_file, include_styles=True)
        print(docx_content_styled)
        print()
