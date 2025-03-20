#!/usr/bin/env python3
import json
import collections
import re

# File paths
INPUT_JSONL = "kaikki.org-dictionary-Korean.jsonl"
OUTPUT_TSV = "dictionary.tsv"
FREQ_FILE = "korean_freq.txt"

def is_single_block(word):
    return len(word) == 1 and "\uAC00" <= word <= "\uD7A3"

def extract_translations(entry):
    translations = []
    if "senses" in entry:
        for sense in entry["senses"]:
            if "glosses" in sense:
                translations.extend(sense["glosses"])
    return translations

def simplify_translations(translations):
    cleaned = []
    for t in translations:
        t = t.strip()
        # E1.3.1: Remove "Short for" entries
        if t.lower().startswith("short for"):
            continue
        # E1.3.4: Remove Chinese characters and junk
        t = re.sub(r'[\u4E00-\u9FFF:]+|\(MC reading.*?\)|Alternative form of|More information|\*', '', t).strip()
        # Skip if empty or no English
        if not t or not any(c.isascii() for c in t):
            continue
        # Keep short phrases (max 3 words)
        if len(t.split()) <= 3:
            # E1.3.2: Filter troublesome entries
            if any(x in t.lower() for x in ["obsolete", "rare", "penis", "shit", "bastard", "(", ")"]):
                continue
            cleaned.append(t)
    # E1.3.2: Return None if no valid translations
    if not cleaned:
        return None
    return ", ".join(cleaned[:3])

def calculate_block_frequencies(jsonl_file):
    block_counts = collections.defaultdict(int)
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line.strip())
            word = entry.get("word", "")
            if len(word) > 1:  # Multi-block words
                for char in word:
                    if is_single_block(char):
                        block_counts[char] += 1
    return block_counts

def main():
    # E1.4: Calculate block frequencies from JSONL
    block_freqs = calculate_block_frequencies(INPUT_JSONL)
    single_blocks = {}

    # Process JSONL for single-block words
    with open(INPUT_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line.strip())
            word = entry.get("word", "")
            if is_single_block(word):
                translations = extract_translations(entry)
                simplified_trans = simplify_translations(translations)
                if simplified_trans is None:
                    continue
                word_freq = 1  # Placeholder
                block_freq = block_freqs.get(word, 0)
                overall_freq = word_freq + block_freq
                single_blocks[word] = (simplified_trans, word_freq, block_freq, overall_freq)

    # E1.5: Sort by overall_freq (descending)
    sorted_blocks = sorted(single_blocks.items(), key=lambda x: x[1][3], reverse=True)

    # Write to TSV
    with open(OUTPUT_TSV, "w", encoding="utf-8") as f:
        f.write("block\ttranslation\tword_freq\tblock_freq\toverall_freq\n")
        for word, (trans, wf, bf, of) in sorted_blocks:
            f.write(f"{word}\t{trans}\t{wf}\t{bf}\t{of}\n")

    print(f"Generated {OUTPUT_TSV} with {len(sorted_blocks)} entries")

if __name__ == "__main__":
    main()