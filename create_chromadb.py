import pandas as pd
import chromadb
import ast # Used for safely evaluating the string representation of lists

# 1. Load the dataset from the CSV file
df = pd.read_csv('video_with_embeddings.csv')

# It's good practice to handle any missing values.
# Here, we drop rows where the 'embedding' column is empty.
df.dropna(subset=['embedding'], inplace=True)

# 2. Convert the string representation of embeddings to a list of floats
# The embeddings in the CSV are stored as strings, e.g., "[-0.1, 0.2, ...]".
# We need to convert these strings into actual lists of numbers.
def parse_embedding(embedding_str):
    try:
        # ast.literal_eval safely evaluates a string containing a Python literal or container display.
        return ast.literal_eval(embedding_str)
    except (ValueError, SyntaxError):
        # If an embedding string is malformed, we'll print a warning
        # and return a vector of zeros. You might want to handle this differently
        # depending on your use case, e.g., by logging the error or skipping the row.
        print(f"Warning: Could not parse embedding string: {embedding_str}")
        # Assuming an embedding dimension of 768, which is common.
        # Adjust this if your embedding dimension is different.
        return [0.0] * 768

df['embedding_list'] = df['embedding'].apply(parse_embedding)

# 3. Initialize ChromaDB and create a collection
# We'll use a persistent client to save the database to a directory on disk.
# This allows you to reuse the collection later without having to rebuild it.
client = chromadb.PersistentClient(path="./chroma_db") # This will save the DB in a "chroma_db" folder

# The collection is where your embeddings and metadata will be stored.
collection_name = "video_embeddings"

# To ensure we start with a fresh collection each time this script is run,
# we'll delete the collection if it already exists.
if collection_name in [c.name for c in client.list_collections()]:
    client.delete_collection(name=collection_name)

collection = client.create_collection(name=collection_name)

# 4. Prepare the data for ChromaDB
# ChromaDB requires the data in specific formats: lists of embeddings, metadatas, and ids.
embeddings = df['embedding_list'].tolist()

# The 'metadatas' will store additional information for each embedding,
# which can be used for filtering or to provide context.
metadatas = df[['id', 'title', 'merged_transcript']].to_dict('records')

# Each item in ChromaDB needs a unique ID. We can use the DataFrame's index for this.
ids = [str(i) for i in df.index]

# 5. Add the data to the collection
# To avoid potential issues with adding a very large dataset at once,
# we'll add the data in smaller batches.
batch_size = 100
for i in range(0, len(ids), batch_size):
    collection.add(
        embeddings=embeddings[i:i+batch_size],
        documents=df['merged_transcript'].iloc[i:i+batch_size].tolist(), # Storing transcript as document
        metadatas=metadatas[i:i+batch_size],
        ids=ids[i:i+batch_size]
    )

print(f"✅ Successfully added {len(ids)} embeddings to the '{collection_name}' collection.")
print("ChromaDB collection is ready for querying.")
print(f"The collection is saved in the './chroma_db' directory.")
print(f"Number of items in the collection: {collection.count()}")