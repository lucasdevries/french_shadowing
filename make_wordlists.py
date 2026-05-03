#!/usr/bin/env python3
"""
Generates vocabulary CSV files from French transcript .txt files.
For each file: extract unique lowercased tokens (strip outer punctuation,
keep mid-word apostrophes), remove pure numbers/empty tokens, sort
alphabetically, then write CSV with header nl,fr.
The Dutch translation column is left as TODO markers for manual review,
but the French word column is fully populated.
"""

import re
import os

BASE = "/Users/lucasdevries/Desktop/GAS french lessons/transcripts_cleaned/"
DEST = "/Users/lucasdevries/Desktop/GAS french lessons/woordenlijsten/"

STRIP_CHARS = '.,?!:;"\'''«»“”‘’()[]'

FILES = [
    "Apprendre le français (FACILEMENT) avec ma Morning Routine (Comprehensible Input).txt",
    "Apprends Le français Chez Moi (Comprehensible Input).txt",
    "Apprends le français Facilement avec ce Vlog (comprehensible input).txt",
]

def extract_words(text):
    tokens = text.split()
    words = set()
    for tok in tokens:
        tok = tok.strip(STRIP_CHARS)
        tok = tok.lower()
        if not tok:
            continue
        # Skip pure numbers (including things like 6h40 we keep, but pure digits we skip)
        if re.fullmatch(r'\d+', tok):
            continue
        # Skip tokens that are only punctuation/symbols
        if re.fullmatch(r'[^\w\']+', tok):
            continue
        words.add(tok)
    return sorted(words)

os.makedirs(DEST, exist_ok=True)

for fname in FILES:
    src_path = BASE + fname
    dst_path = DEST + fname.replace(".txt", ".csv")
    with open(src_path, encoding="utf-8") as f:
        text = f.read()
    words = extract_words(text)
    print(f"\n{fname}")
    print(f"  {len(words)} unique words")
    for w in words:
        print(f"  {w}")
    with open(dst_path, "w", encoding="utf-8") as out:
        out.write("nl,fr\n")
        for w in words:
            out.write(f",{w}\n")
    print(f"  -> Written to {dst_path}")

print("\nDone. Dutch translations (nl column) need to be filled in.")
