import chromadb
import sys

DB_PATH = "chroma"
COLLECTION = "Pheme-news"

client = chromadb.PersistentClient(path=DB_PATH)
coll = client.get_or_create_collection(COLLECTION)

results = coll.query(
    query_texts=[f"{sys.argv[1]}"],
    n_results=2,
    # where={"metadata_field": "is_equal_to_this"}, # optional filter
    # where_document={"$contains":"search_string"}  # optional filter
)
l = len(results["documents"][0])
for i in range(l):
    print(f"{results['ids'][0][i]}\n{results['documents'][0][i]}\n\n")
