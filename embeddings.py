#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
import os
import gc

def chunk_text(text, max_chars=1000, overlap=200):
    text = str(text).strip()
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        start += max_chars - overlap
    return chunks

def embed_streaming(input_csv, out_parquet, model_name, chunk_chars, overlap, batch_size, device):
    print(f"🧠 Loading model: {model_name} on {device}")
    model = SentenceTransformer(model_name, device=device)

    print(f"📂 Opening input file: {input_csv}")
    reader = pd.read_csv(input_csv, chunksize=20)
    all_rows = []

    os.makedirs(os.path.dirname(out_parquet), exist_ok=True)

    for chunk in tqdm(reader, desc="Embedding chunks"):
        for _, row in chunk.iterrows():
            title = str(row.get("title", ""))
            description = str(row.get("description", ""))
            text = f"{title}. {description}".strip()
            pieces = chunk_text(text, chunk_chars, overlap)

            try:
                embeddings = model.encode(
                    pieces,
                    batch_size=batch_size,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                avg_embedding = np.mean(embeddings, axis=0)
                row_out = row.to_dict()
                row_out["embedding"] = avg_embedding.tolist()
                all_rows.append(row_out)
            except Exception as e:
                print(f"⚠️ Error embedding row: {e}")

        if len(all_rows) >= 50:
            df_out = pd.DataFrame(all_rows)
            if os.path.exists(out_parquet):
                df_existing = pd.read_parquet(out_parquet)
                df_combined = pd.concat([df_existing, df_out], ignore_index=True)
                df_combined.to_parquet(out_parquet, index=False, engine="pyarrow", compression="snappy")
            else:
                df_out.to_parquet(out_parquet, index=False, engine="pyarrow", compression="snappy")
            all_rows = []
            gc.collect()

    # Final flush
    if all_rows:
        df_out = pd.DataFrame(all_rows)
        if os.path.exists(out_parquet):
            df_existing = pd.read_parquet(out_parquet)
            df_combined = pd.concat([df_existing, df_out], ignore_index=True)
            df_combined.to_parquet(out_parquet, index=False, engine="pyarrow", compression="snappy")
        else:
            df_out.to_parquet(out_parquet, index=False, engine="pyarrow", compression="snappy")

    print(f"✅ Embedding complete. Results saved to {out_parquet}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out_parquet", required=True)
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--chunk_chars", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=200)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    embed_streaming(
        input_csv=args.input,
        out_parquet=args.out_parquet,
        model_name=args.model,
        chunk_chars=args.chunk_chars,
        overlap=args.overlap,
        batch_size=args.batch_size,
        device=args.device,
    )
