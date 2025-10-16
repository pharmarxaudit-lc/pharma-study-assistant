from typing import Dict, List

import fitz


class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)

    def extract_all(self) -> List[Dict]:
        pages_data = []
        for page_num in range(self.total_pages):
            page_data = self.extract_page(page_num)
            pages_data.append(page_data)
        return pages_data

    def extract_page(self, page_num: int) -> Dict:
        page = self.doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        text_content = []
        headers = []

        for block in blocks:
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    line_text = ""
                    max_size = 0

                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        max_size = max(max_size, span.get("size", 0))

                    line_text = line_text.strip()
                    if line_text:
                        is_header = max_size > 14 or (line_text.isupper() and len(line_text) > 3)
                        if is_header:
                            headers.append(line_text)
                        text_content.append({
                            "text": line_text,
                            "size": max_size,
                            "is_header": is_header
                        })

        return {
            "page": page_num + 1,
            "content": text_content,
            "headers": headers,
            "full_text": page.get_text()
        }

    def close(self):
        self.doc.close()
