from sentence_transformers import SentenceTransformer
import weaviate
from weaviate.classes.init import Auth
import sys
sys.stdout.reconfigure(encoding='utf-8')

class WeaviateRetriver():
    def __init__(self, url, api_key):
        self.vectordb_client = weaviate.connect_to_weaviate_cloud(cluster_url=url,
                                                         auth_credentials=Auth.api_key(api_key))
        self.embedding_model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True, device='cpu')

    def format_docs(self, docs):
            return "\n\n".join(doc.page_content for doc in docs)

    def search(self,query,k):
        try:
            query_embedding = self.embedding_model.encode(query)
            collection = self.vectordb_client.collections.get("Documents")
            result = collection.query.hybrid(query= query,vector = query_embedding,limit = k)
            docs=[]
            for content in result.objects:
                docs.append(f"Tài liệu {content.properties['file']}: " + content.properties['text'])
        finally:
            self.vectordb_client.close()
        return docs