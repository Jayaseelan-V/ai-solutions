import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
import chromadb.utils.embedding_functions as embedding_functions

#openai_key=os.environ.get("OPENAI_API_KEY")

"""
openai_embfun = embedding_functions.OpenAIEmbeddingFunction(
    api_key = openai_key,
    model_name = "text-embedding-ada-002"
)
"""
load_dotenv()

collection_name = os.getenv("collection_name")
api_key=os.getenv("api_key")
model_name=os.getenv("model_name")
base_url=os.getenv("base_url")


chroma_client = chromadb.PersistentClient(path="chroma_db_storage")
#collection = chroma_client.get_or_create_collection(name=collection_name), embedding_function=openai_embfun)
collection = chroma_client.get_or_create_collection(name=collection_name)

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

"""
results = collection.query(
    query_texts=["world1"],    
    n_results= 1
)
"""

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

"""
results = client.chat.completions.create (
    messages= [
        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Write a program to get sum of two numbers in python",
        }
    ],
    model=model_name
)

#print(results.choices[0].message.content)
"""

def query_document(query):
    results = collection.query(
    query_texts=[query],    
    n_results= 2)
    relevant_chunks = [doc for docs in results["documents"] for doc in docs]
    #print(relevant_chunks)
    return relevant_chunks

def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )
    response = client.chat.completions.create (
        messages= [
            {
                "role": "system",
                "content":  prompt
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=model_name
    )
    return response.choices[0].message.content


while True:
    question  = input("Enter your query here : ")
    if question == "<quit>":
        break
    else:
       print(generate_response(question,query_document(question)))