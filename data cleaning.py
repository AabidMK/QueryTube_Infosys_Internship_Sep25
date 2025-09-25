import pandas as pd
import re

# Load CSV
df = pd.read_csv("all_transcripts.csv")

# Drop empty transcripts
df = df.dropna(subset=["transcript"])

def clean_text(text):
    # Remove [Music] or anything inside []
    text = re.sub(r"\[.*?\]", " ", text)

    # Remove filler words (extend list if needed)
    fillers = ["oh my god", "uh", "um", "you know", "like", "alright"]
    for f in fillers:
        text = re.sub(rf"\b{f}\b", "", text, flags=re.IGNORECASE)

    # Remove duplicate consecutive words (e.g., "take take")
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)

    # Remove extra spaces, tabs, newlines
    text = re.sub(r"\s+", " ", text).strip()

    return text

# Replace transcript with cleaned text
df["transcript"] = df["transcript"].apply(clean_text)

# Save back without old messy version (only cleaned one stays)
df.to_csv("transcript_cleaned.csv", index=False)
print("Cleaning done! Saved as transcript_cleaned.csv")
