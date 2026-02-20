import os
import pandas as pd
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# =========================
# CONFIG
# =========================
CSV_FILE = r"C:\Users\HP\Downloads\GOLD.csv"
DB_LOCATION = "./chroma_gold_price_db"
COLLECTION_NAME = "gold_price_history"
BATCH_SIZE = 1000

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(CSV_FILE)

# =========================
# EMBEDDING MODEL
# =========================
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# =========================
# VECTOR STORE
# =========================
vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=DB_LOCATION,
    embedding_function=embeddings
)

existing_count = vector_store._collection.count()
print("Existing documents in DB:", existing_count)

# =========================
# PREPARE DOCUMENTS
# =========================
documents = []
ids = []

for i, row in df.iterrows():
    content = (
        f"On {row['Date']}, gold opened at {row['Open']} USD, "
        f"reached a high of {row['High']} USD, "
        f"a low of {row['Low']} USD, "
        f"and closed at {row['Close']} USD. "
        f"Trading volume was {row['Volume']}."
    ) 
 
    doc = Document(
        page_content=content,
        metadata={
            "date": row["Date"]
        },
        id=str(i)
    )

    documents.append(doc)
    ids.append(str(i))

# =========================
# INGEST (ONLY IF EMPTY)
# =========================
if existing_count == 0:
    print("Ingesting documents into Chroma...")

    for i in range(0, len(documents), BATCH_SIZE):
        batch_docs = documents[i:i + BATCH_SIZE]
        batch_ids = ids[i:i + BATCH_SIZE]

        vector_store.add_documents(
            documents=batch_docs,
            ids=batch_ids
        )

        print(f"Inserted documents {i} to {i + len(batch_docs)}")

    print("Final document count:", vector_store._collection.count())
else:
    print("Using existing embeddings. No re-ingestion needed.")

# =========================
# RETRIEVER
# =========================
retriever = vector_store.as_retriever(
    search_kwargs={"k": 15}
)