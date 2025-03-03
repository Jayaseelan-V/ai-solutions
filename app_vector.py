import chromadb
import os
from chromadb.utils import embedding_functions


#openai_apikey = os.environ.get("OPENAI_API_KEY")


collection_name = "test_collection"

#openai embedding functions.
"""
open_emb_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key = openai_apikey,
    model_name = "text-embedding-ada-002"
)
"""


#chroma_client = chromadb.Client()
chroma_client = chromadb.PersistentClient(path="chromadb_vector")

collection = chroma_client.get_or_create_collection(name=collection_name)#, embedding_function= open_emb_fn)

print(chroma_client.list_collections())



documents = [
    {"id": "doc1", "text": "Hello, world"},
    {"id": "doc2", "text": "what is your age?"},
    {"id": "doc3", "text": "How old are you?"},
]

for doc in documents:
    collection.upsert(
        documents=[doc["text"]],
        ids=doc["id"]
    )

while True:
    query_text = input()
    if(query_text == "<quit>"):
        break
    else:
        results = collection.query(
            query_texts=[query_text],
            n_results=1
        )
        print(results)