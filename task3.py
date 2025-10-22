#!/usr/bin/env python3
"""
task3.py  (fixed)

Same functionality as before: cleans video metadata and transcripts.
Fixed pandas.read_csv call to avoid passing unsupported `errors` kwarg.
"""

import argparse
import os
import re
import unicodedata
import logging
import pandas as pd
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------------- regex patterns ----------------
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")
TIMESTAMP_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
BRACKET_RE = re.compile(r"\[.*?\]")
KEEP_RE = re.compile(r"[^0-9A-Za-z\s\-\_\,\.\'\"/():]+")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")

# ---------------- helper cleaning functions ----------------
def remove_emojis(text: str) -> str:
    if not isinstance(text, str) or not text:
        return "" if text is None else str(text)
    return EMOJI_PATTERN.sub(" ", text)

def remove_html(text: str) -> str:
    if not isinstance(text, str) or not text:
        return "" if text is None else str(text)
    return HTML_TAG_RE.sub(" ", text)

def remove_timestamps_and_brackets(text: str) -> str:
    if not isinstance(text, str) or not text:
        return "" if text is None else str(text)
    text = TIMESTAMP_RE.sub(" ", text)
    text = BRACKET_RE.sub(" ", text)
    return text

def remove_special_chars_keep_basic(text: str) -> str:
    if not isinstance(text, str) or not text:
        return "" if text is None else str(text)
    text = text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    text = CONTROL_RE.sub(" ", text)
    text = KEEP_RE.sub(" ", text)
    return text

def normalize_whitespace_and_lower(text: Optional[str]) -> str:
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()

# ---------------- dataset-specific cleaning ----------------
def clean_video_row(text: Optional[str]) -> str:
    if text is None:
        return ""
    text = remove_html(text)
    text = remove_emojis(text)
    text = remove_special_chars_keep_basic(text)
    text = normalize_whitespace_and_lower(text)
    return text

def clean_transcript_row(text: Optional[str]) -> str:
    if text is None:
        return ""
    if isinstance(text, str):
        text = text.replace("\r", " ").replace("\n", " ")
    text = remove_timestamps_and_brackets(text)
    text = remove_emojis(text)
    text = remove_special_chars_keep_basic(text)
    text = normalize_whitespace_and_lower(text)
    return text

# ---------------- column detection ----------------
def find_column(df: pd.DataFrame, candidates):
    lc = {c.lower(): c for c in df.columns}
    for cand in candidates:
        cand_l = cand.lower()
        if cand_l in lc:
            return lc[cand_l]
    for col in df.columns:
        lcol = col.lower()
        for cand in candidates:
            if cand.lower() in lcol:
                return col
    return None

# ---------------- processing functions ----------------
def read_csv_with_replacement(path: str) -> pd.DataFrame:
    """
    Open file using encoding='utf-8' and errors='replace' (so invalid bytes are replaced),
    then pass the file handle to pd.read_csv().
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        df = pd.read_csv(fh, dtype=str)
    return df

def process_video_csv(input_path: str, output_path: str, ensure_title_unique: bool = True):
    logging.info(f"Reading video CSV: {input_path}")
    df = read_csv_with_replacement(input_path)
    if df.empty:
        logging.warning("Video CSV is empty. Writing an empty cleaned file.")
        df.to_csv(output_path, index=False)
        return

    video_id_col = find_column(df, ["video_id", "id", "vid", "videoid"]) or df.columns[0]
    title_col = find_column(df, ["title", "video_title", "name", "heading"])
    if not title_col:
        raise ValueError("Could not find a title column in video CSV. Columns: " + ", ".join(df.columns))
    desc_col = find_column(df, ["description", "desc", "details", "summary"])

    cleaned_title_col = title_col + "_clean"
    df[cleaned_title_col] = df[title_col].apply(clean_video_row)

    if desc_col:
        cleaned_desc_col = desc_col + "_clean"
        df[cleaned_desc_col] = df[desc_col].apply(clean_video_row)
    else:
        cleaned_desc_col = None

    if ensure_title_unique:
        counts = df.groupby(cleaned_title_col)[video_id_col].nunique()
        duplicates = counts[counts > 1].index.tolist()
        if duplicates:
            logging.info(f"Found {len(duplicates)} cleaned-title(s) used by multiple video_ids. Appending video_id to those titles.")
            mask = df[cleaned_title_col].isin(duplicates)
            df.loc[mask, cleaned_title_col] = df.loc[mask, cleaned_title_col].astype(str) + " - " + df.loc[mask, video_id_col].astype(str)

    df[cleaned_title_col] = df[cleaned_title_col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    if cleaned_desc_col:
        df[cleaned_desc_col] = df[cleaned_desc_col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    df.to_csv(output_path, index=False, encoding="utf-8")
    logging.info(f"Saved cleaned video CSV to: {output_path}")

def process_transcript_csv(input_path: str, output_path: str):
    logging.info(f"Reading transcript CSV: {input_path}")
    df = read_csv_with_replacement(input_path)
    if df.empty:
        logging.warning("Transcript CSV is empty. Writing an empty cleaned file.")
        df.to_csv(output_path, index=False)
        return

    video_id_col = find_column(df, ["video_id", "id", "vid", "videoid"]) or df.columns[0]
    transcript_col = find_column(df, ["transcript", "text", "caption", "captions", "subtitle", "subtitles"])
    if not transcript_col:
        raise ValueError("Could not find a transcript column in transcript CSV. Columns: " + ", ".join(df.columns))

    df[transcript_col] = df[transcript_col].fillna("")
    df["transcript_status"] = df[transcript_col].apply(lambda x: "missing" if (not isinstance(x, str) or x.strip() == "") else "present")

    cleaned_transcript_col = transcript_col + "_clean"
    df[cleaned_transcript_col] = df[transcript_col].apply(clean_transcript_row)
    df[cleaned_transcript_col] = df[cleaned_transcript_col].apply(lambda x: re.sub(r"\s+", " ", x).strip() if isinstance(x, str) else x)

    df.to_csv(output_path, index=False, encoding="utf-8")
    logging.info(f"Saved cleaned transcript CSV to: {output_path}")

# ---------------- CLI / main ----------------
def main():
    parser = argparse.ArgumentParser(description="Clean video metadata and transcript CSVs.")
    parser.add_argument("--video", default="master_task1_datset.csv", help="path to video CSV (default: master_task1_datset.csv)")
    parser.add_argument("--transcript", default="master_task2_datset.csv", help="path to transcript CSV (default: master_task2_datset.csv)")
    parser.add_argument("--out_video", default=None, help="output path for cleaned video CSV")
    parser.add_argument("--out_transcript", default=None, help="output path for cleaned transcript CSV")
    parser.add_argument("--no_ensure_title_unique", action="store_true", help="disable automatic uniqueness enforcement on titles")
    args = parser.parse_args()

    video_in = args.video
    transcript_in = args.transcript

    if not os.path.exists(video_in):
        logging.error(f"Video CSV not found: {video_in}")
        raise SystemExit(1)
    if not os.path.exists(transcript_in):
        logging.error(f"Transcript CSV not found: {transcript_in}")
        raise SystemExit(1)

    out_video = args.out_video or os.path.join(os.path.dirname(video_in), "cleaned_" + os.path.basename(video_in))
    out_transcript = args.out_transcript or os.path.join(os.path.dirname(transcript_in), "cleaned_" + os.path.basename(transcript_in))

    try:
        process_video_csv(video_in, out_video, ensure_title_unique=not args.no_ensure_title_unique)
        process_transcript_csv(transcript_in, out_transcript)
    except Exception as e:
        logging.exception("Processing failed:")
        raise SystemExit(1)

    try:
        logging.info("Sample of cleaned video CSV:")
        print(pd.read_csv(out_video, nrows=5).to_string(index=False))
    except Exception:
        pass

    try:
        logging.info("Sample of cleaned transcript CSV:")
        print(pd.read_csv(out_transcript, nrows=5).to_string(index=False))
    except Exception:
        pass

if __name__ == "__main__":
    main()
