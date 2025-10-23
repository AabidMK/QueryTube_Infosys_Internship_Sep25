import requests
from tabulate import tabulate  # optional, for nice table output

# -------------------------------
# Configuration
# -------------------------------
API_URL = "http://127.0.0.1:8000/search"  # your current API endpoint

# List of test queries
test_queries = [
    {"query": "python tutorial", "top_k": 5, "min_similarity": 0.5},
    {"query": "dont learn python", "top_k": 5, "min_similarity": 0.5},
    {"query": "how to make pasta", "top_k": 5, "min_similarity": 0.5},
    {"query": "flask tutorial", "top_k": 5, "min_similarity": 0.5},
    {"query": "machine learning basics", "top_k": 5, "min_similarity": 0.5},
    {"query": "javascript guide", "top_k": 5, "min_similarity": 0.5},
    {"query": "how we can cook", "top_k": 5, "min_similarity": 0.5},  # likely no match
]

# -------------------------------
# Function to test API
# -------------------------------
def test_search_api():
    print("Running automated API tests...\n")
    
    for i, q in enumerate(test_queries, start=1):
        print(f"Test {i}: '{q['query']}'\n" + "-"*50)
        response = requests.post(API_URL, json=q)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                for item in results:
                    print(f"Rank: {item['rank']}")
                    print(f"Title: {item['title']}")
                    print(f"Channel: {item['channel']}")
                    print(f"Similarity: {item['similarity']}")
                    print(f"Video URL: {item['video_url']}")
                    print(f"Thumbnail URL: {item['thumbnail_url']}")
                    print("-"*50)
            else:
                print("No results found.")
            print(f"Average Similarity: {data.get('average_similarity',0)}")
            print(f"Relevance: {data.get('relevance','Weak')}")
        else:
            print("Error:", response.status_code, response.text)
        print("\n")

# -------------------------------
# Run tests
# -------------------------------
if __name__ == "__main__":
    test_search_api()
