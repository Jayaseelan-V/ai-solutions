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

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

default_ef = embedding_functions.DefaultEmbeddingFunction()


chroma_client = chromadb.PersistentClient(path="chroma_db_storage")
#collection = chroma_client.get_or_create_collection(name=collection_name), embedding_function=openai_embfun)
collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=default_ef)



"""
documents = [
    {"id": "doc1", "text": "Hello, world"},
    {"id": "doc2", "text": "what is your age?"},
    {"id": "doc3", "text": "How old are you?"},
]"""



def load_documents(path):
    documents = []
    for filename in os.listdir(path):
        with open(file=os.path.join(path,filename), mode="r", encoding="utf-8") as file:
            documents.append(
                {
                    "id":filename,
                    "text": file.read()
                })
    return documents

def split_text(text, chunk_size=1000, chunk_overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks

       
documents  = load_documents("./news_articles")


for doc in documents:
    chunks = split_text(doc["text"])
    
    for i, chunk in enumerate(chunks):
        #embedding_response = client.embeddings.create(input=chunk, model="")
        #print(default_ef([chunk]))
        collection.upsert(
            documents=[chunk],        
            ids=f"{doc["id"]}_chunk_{i+1}",
            embeddings=default_ef([chunk])
        )

"""
results = collection.query(
    query_texts=["world1"],    
    n_results= 1
)
"""





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
    n_results= 5)
    relevant_chunks = [doc for docs in results["documents"] for doc in docs]    
    return relevant_chunks

def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )
    print(prompt)
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