import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--transcripts", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--lang", default="en")
    args = parser.parse_args()

    print("📂 Loading metadata...")
    meta = pd.read_csv(args.metadata)
    print("📂 Loading transcripts...")
    trans = pd.read_csv(args.transcripts, encoding="utf-8", on_bad_lines="skip")

    # Standardize ID column names
    if "video_id" not in meta.columns and "id" in meta.columns:
        meta.rename(columns={"id": "video_id"}, inplace=True)
    if "video_id" not in trans.columns and "id" in trans.columns:
        trans.rename(columns={"id": "video_id"}, inplace=True)

    print("🔗 Merging on video_id...")
    df = pd.merge(meta, trans, on="video_id", how="inner")

    # Drop duplicates
    df = df.drop_duplicates(subset=["video_id"])

    # Save as CSV, preserving NaN values
    df.to_csv(args.out, index=False, na_rep="NaN")

    print(f"✅ Saved merged dataset with NaNs preserved → {args.out}")

if __name__ == "__main__":
    main()

