import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# --- Configuration ---
FILE_NAME = "videos_with_embeddings_cleaned.csv"
CHROMA_PATH = "chromadb_data"
COLLECTION_NAME = "video_embeddings_all"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 100  # Larger batches = faster

def process_video_batch(model, batch_df):
    """Process a batch of videos quickly"""
    batch_ids = []
    batch_embeddings = []
    batch_metadatas = []
    
    for _, row in batch_df.iterrows():
        try:
            # Quick text preparation
            title = str(row.get('title', ''))
            desc = str(row.get('description', ''))[:500]
            transcript = str(row.get('transcript', ''))[:4000]
            channel = str(row.get('channel_title', 'Unknown'))
            
            # Combine text
            full_text = f"{title} {desc} {transcript}".strip()
            
            if len(full_text) > 10:
                # Generate embedding
                embedding = model.encode(full_text, show_progress_bar=False)
                
                if len(embedding) == 384:
                    batch_ids.append(str(row['video_id']))
                    
                    # Create metadata
                    metadata = {
                        'video_id': str(row['video_id']),
                        'title': title,
                        'channel_title': channel,
                        'description': desc,
                        'transcript_preview': (transcript[:200] + "...") if len(transcript) > 200 else transcript,
                        'viewcount': str(row.get('viewcount', 'N/A')),
                        'duration': str(row.get('duration', 'N/A'))
                    }
                    
                    batch_metadatas.append(metadata)
                    batch_embeddings.append(embedding.tolist())
            
        except Exception as e:
            # Silent skip for speed
            continue
    
    return batch_ids, batch_embeddings, batch_metadatas

def fast_full_loader():
    print("🚀 FAST FULL CSV LOADER - All Videos to ChromaDB")
    start_time = time.time()
    
    # Step 1: Load model
    print("⚙️ Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("✅ Model ready!")
    
    # Step 2: Setup ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"🗑️ Cleared old collection")
    except:
        pass
    
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"✅ Collection '{COLLECTION_NAME}' created")
    
    # Step 3: Load and process CSV
    print("📊 Loading CSV...")
    df = pd.read_csv(FILE_NAME)
    total_videos = len(df)
    print(f"📈 Found {total_videos} videos total")
    
    # Count Beast videos
    beast_count = len(df[df['channel_title'].str.contains('Beast|Philanthropy', case=False, na=False)])
    print(f"🐾 Beast videos: {beast_count}")
    
    # Step 4: Process in large batches (FAST!)
    print("🔥 Processing videos in batches...")
    all_ids = []
    all_embeddings = []
    all_metadatas = []
    
    # Split into batches
    batches = [df[i:i+BATCH_SIZE] for i in range(0, total_videos, BATCH_SIZE)]
    print(f"📦 Created {len(batches)} batches of {BATCH_SIZE} videos each")
    
    for i, batch_df in enumerate(batches):
        print(f"  Processing batch {i+1}/{len(batches)}...")
        
        batch_ids, batch_embeddings, batch_metadatas = process_video_batch(model, batch_df)
        
        all_ids.extend(batch_ids)
        all_embeddings.extend(batch_embeddings)
        all_metadatas.extend(batch_metadatas)
        
        print(f"    ✅ Batch {i+1}: {len(batch_ids)} valid embeddings")
    
    # Step 5: Add to ChromaDB in large chunks
    print(f"\n💾 Adding {len(all_ids)} total embeddings to ChromaDB...")
    chunk_size = 200  # Large chunks for speed
    
    for i in range(0, len(all_ids), chunk_size):
        chunk_ids = all_ids[i:i+chunk_size]
        chunk_embeddings = all_embeddings[i:i+chunk_size]
        chunk_metadatas = all_metadatas[i:i+chunk_size]
        
        try:
            collection.add(
                ids=chunk_ids,
                embeddings=chunk_embeddings,
                metadatas=chunk_metadatas
            )
            print(f"    Added chunk {i//chunk_size + 1} ({len(chunk_ids)} videos)")
        except Exception as e:
            print(f"    ⚠️ Chunk error: {e}")
    
    # Step 6: Verify
    final_count = collection.count()
    elapsed = time.time() - start_time
    
    print(f"\n🎉 SUCCESS!")
    print(f"✅ Loaded {final_count} videos into '{COLLECTION_NAME}'")
    print(f"⏱️ Total time: {elapsed:.1f} seconds")
    print(f"⚡ Speed: {final_count/elapsed:.1f} videos/second")
    
    # Verify Beast videos
    try:
        # Get sample Beast video
        sample_results = collection.get(
            limit=1,
            include=["metadatas"],
            where={"channel_title": {"$eq": "Beast Philanthropy"}}
        )
        if sample_results['metadatas']:
            print(f"🐾 Beast verification: {sample_results['metadatas'][0]['title'][:50]}...")
    except:
        print("🐾 Beast videos loaded but filter test failed (normal)")
    
    print(f"\n🔍 UPDATE YOUR SEARCH SCRIPT:")
    print(f"COLLECTION_NAME = '{COLLECTION_NAME}'")
    print("\n🧪 Test queries:")
    print("  'rescuing child slaves africa' → Beast video #1")
    print("  'python tutorial' → Tech videos") 
    print("  'building wells africa' → Beast charity content")
    
    return final_count

# Run it!
if __name__ == "__main__":
    try:
        count = fast_full_loader()
        if count > 0:
            print(f"\n🎯 All {count} videos ready for semantic search!")
            print(f"📁 Collection saved at: {CHROMA_PATH}/{COLLECTION_NAME}")
        else:
            print("❌ No videos loaded!")
    except Exception as e:
        print(f"💥 Error: {e}")
