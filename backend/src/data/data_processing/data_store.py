import os
from sentence_transformers import SentenceTransformer
import weaviate
from weaviate.classes.init import Auth
from data_preprocess import PdfReader, DotTextSplitter, OCR
from dotenv import load_dotenv
load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

class Uploader():
    """Tải dữ liệu lên Weaviate"""
    def __init__(self):
        self.client = weaviate.Client(cluster_url=WEAVIATE_URL,
                                      auth_credentials=Auth.api_key(api_key=WEAVIATE_API_KEY))
        self.collection = self.client.collections.get("documents")
        self.embedding_model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True, device='cpu')

    def upload(self,pdf_file,text):
        if self.client.is_ready():
            embedding = self.embedding_model.encode(text)
            self.collection.data.insert(properties={
                                                    "file": pdf_file,
                                                    "text":text
                                                },
                                        vector = embedding)

def main():
    pdf_folder_path = r""
    reader = PdfReader()
    splitter = DotTextSplitter()
    uploader = Uploader()
    for pdf_file in os.listdir(pdf_folder_path):
        if pdf_file.endswith(".pdf"):
            text = reader.extract_pdf(pdf_folder_path + '\\' + pdf_file)
        elif pdf_file.endswith(".txt"):
            with open(pdf_folder_path + '\\' + pdf_file, "r", encoding="utf-8") as f:
                text = f.read()

        if len(text.strip(" ")) == 0:
            ocr = OCR()
            text = ocr.ocr_pdf(pdf_folder_path + '\\' + pdf_file)
        chunks = splitter.split_text(text)
        for chunk in chunks:
            uploader.upload(pdf_file, chunk)
                
if __name__ == "__main__":
    main()