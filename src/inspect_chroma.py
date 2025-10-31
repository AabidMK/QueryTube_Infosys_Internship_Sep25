import chromadb

print("🔍 Inspecting ChromaDB collection...\n")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./data/chroma_db")

# List collections
collections = [c.name for c in client.list_collections()]
print(f"📁 Available collections: {collections}")

if "youtube_videos" not in collections:
    print("⚠️ Collection 'youtube_videos' not found.")
else:
    collection = client.get_collection("youtube_videos")
    count = collection.count()
    print(f"\n✅ Collection 'youtube_videos' found with {count} embeddings.\n")

    if count > 0:
        print("📄 Fetching a few sample documents...\n")
        docs = collection.peek()
        for i, (doc, meta) in enumerate(zip(docs['documents'], docs['metadatas'])):
            print(f"{i+1}. 🎬 Title: {meta.get('title', 'N/A')}")
            print(f"   🧩 Segment: {meta.get('segment', 'N/A')}")
            print(f"   🗒️ Text: {doc[:200]}...\n")
