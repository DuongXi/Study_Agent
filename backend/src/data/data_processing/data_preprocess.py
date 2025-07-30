from google import genai
import os
from typing import List
import pdfplumber
from langchain.text_splitter import TextSplitter
from dotenv import load_dotenv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.src.agent.prompt import OCR_PROMPT

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class OCR():
    """Đọc file pdf scan"""
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_id = "gemini-2.0-flash"
        self.ocr_prompt = OCR_PROMPT
    
    def ocr_pdf(self,file_path):
        file = self.client.files.upload(file=file_path)
        response = self.client.models.generate_content(model=self.model_id, 
                                                       contents=[self.ocr_prompt, file], 
                                                       config={
                                                           "response_mime_type":"text/plain",
                                                            "temperature": 0
                                                        }
                                                    )
        self.client.files.delete(name=file.name)
        return response.text

class PdfReader():
    """Đọc file pdf"""
    def __init__(self):
        pass
    
    def table_to_markdown(self, table):
        # Chuyển đổi bảng thành markdown
        table_lines = []
        for i, row in enumerate(table):
            cleaned_row = [cell if cell else "" for cell in row]
            table_lines.append("| " + " | ".join(cleaned_row) + " |")
            if i == 0:
                table_lines.append("| " + " | ".join(["---" for _ in row]) + " |")
        return "\n".join(table_lines)
    
    def extract_pdf(self, pdf_path):
        contents = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                
                # Trích xuất văn bản và bảng với tọa độ
                content = []
                
                # Trích xuất các dòng văn bản
                for line in page.extract_text_lines():
                    content.append((line['top'], "text", line['text']))
                
                # Trích xuất bảng
                for table in page.find_tables():
                    table_content = table.extract()
                    markdown_table = self.table_to_markdown(table_content)
                    content.append((table.bbox[1], "table", markdown_table))
                
                content.sort(key=lambda x: x[0])
                
                for _, type_, data in content:
                    if type_ == "text":
                        contents += (data+"\n")
                    elif type_ == "table":
                        contents += (data+"\n")
        return contents

class DotTextSplitter(TextSplitter):
    """Lớp tuỳ chỉnh để chia văn bản theo câu"""
    def __init__(self, chunk_size : int = 1000, chunk_overlap : int = 200, keep_separator : bool = True):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.keep_separator = keep_separator

    def split_text(self, text : str) -> List[str]:
        if not text:
            return []

        sentences = text.split(".")
        
        if self.keep_separator:
            sentences = [s.strip() + "." for s in sentences if s.strip()]
        else:
            sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
                while len(current_chunk) > self.chunk_size:
                    split_point = current_chunk.rfind(" ", 0, self.chunk_size)
                    if split_point == -1: 
                        split_point = self.chunk_size
                    chunks.append(current_chunk[:split_point])
                    current_chunk = current_chunk[split_point:].strip()

            if self.chunk_overlap > 0 and len(chunks) > 0 and current_chunk == sentence:
                overlap_text = chunks[-1][-self.chunk_overlap:]
                current_chunk = overlap_text + " " + current_chunk
                
        if current_chunk:
            chunks.append(current_chunk)

        return chunks