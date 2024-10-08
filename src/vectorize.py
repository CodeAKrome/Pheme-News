import chromadb
import sys
from tqdm import tqdm
from json import loads, JSONDecodeError


DB_PATH="chroma"
COLLECTION = "Pheme-news"
# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
# client = chromadb.Client()

client = chromadb.PersistentClient(path=DB_PATH)
coll = client.get_or_create_collection(COLLECTION)

for line in tqdm(sys.stdin):
    line = line.strip()
    if not line: continue
    try:
        data = loads(line)
    except JSONDecodeError as e:
        sys.stderr.write(f"JSON: {e}\n{line}\n")
        continue
    # This should mean this is an rss flavored record
    if not 'ner' in data:
        print(line)
        continue

    # Should have a valid record now. Let's extract the data we need:
    id = data['id']
    text = data['text']
    source = data['source']
    link = data['link']
    tags = data['tags']
    ner = data['ner']

    meta = {"source": source, "link": link}
    for tag in tags:
        meta[f"tag/{tag}"] = "1"

    for ent in ner:
        for span in ent['spans']:
            spankey = f"{span['value']}/{span['text']}"
            if spankey in meta:
                meta[spankey] += 1
            else:
                meta[spankey] = 1
                
    coll.add(
        documents=[text], # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
        metadatas=[meta], # filter on these!
        ids=[f"{id}"], # unique for each doc
    )

# Query/search 2 most similar results. You can also .get by id
# results = collection.query(
#     query_texts=["This is a query document"],
#     n_results=2,
#     # where={"metadata_field": "is_equal_to_this"}, # optional filter
#     # where_document={"$contains":"search_string"}  # optional filter
# )