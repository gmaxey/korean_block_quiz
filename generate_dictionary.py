#!/usr/bin/env python3
import json
import csv
import urllib.request
import re
from unicodedata import normalize
from collections import defaultdict

URL = "https://kaikki.org/dictionary/Korean/kaikki.org-dictionary-Korean.jsonl"
FREQ_LIST_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ko/ko_full.txt"

def is_single_block(word):
    return len(word) == 1 and "\uAC00" <= word <= "\uD7A3"

def clean_translations(raw_translations):
    parts = raw_translations.split(";")
    cleaned = []
    # Regex to match Hanja (CJK ideographs) followed by colon and optional space
    hanja_pattern = re.compile(r'[\u4E00-\u9FFF]+:\s*')
    
    for part in parts:
        part = part.strip()
        # Skip unwanted metadata
        if not part or any(x in part.lower() for x in [
            "(eumhun reading", "(mc reading", "infinitive of", "adnominal of", 
            "interrogative of", "hortative of", "imperative of", "cause/reason of",
            "alternative form", "synonym of", "contraction of", "short for"
        ]):
            continue
        # Remove Hanja and colon, keep the rest
        cleaned_part = hanja_pattern.sub('', part)
        if cleaned_part:
            cleaned.append(cleaned_part)
    
    return ";".join(cleaned).strip(";") or "unknown"

def load_word_frequencies():
    freq_dict = {}
    try:
        with urllib.request.urlopen(FREQ_LIST_URL) as response:
            for line in response:
                word, freq = line.decode("utf-8").strip().split(" ", 1)
                if is_single_block(word):
                    freq_dict[word] = int(freq)
        print(f"Loaded frequency list from {FREQ_LIST_URL}")
    except Exception as e:
        print(f"Failed to load frequency list: {e}. Using defaults (10, 20).")
    return freq_dict

def calculate_block_frequencies():
    block_freq = defaultdict(int)
    with urllib.request.urlopen(URL) as response:
        for line in response:
            entry = json.loads(line.decode("utf-8").strip())
            word = entry.get("word", "")
            for char in word:
                if is_single_block(char):
                    block_freq[char] += 1
    return block_freq

def aggregate_entries(word_freq_dict, block_freq_dict):
    block_data = defaultdict(lambda: {"translations": set(), "word_freq": 10, "block_freq": 20})
    
    with urllib.request.urlopen(URL) as response:
        for line in response:
            entry = json.loads(line.decode("utf-8").strip())
            word = entry.get("word", "")
            
            if not is_single_block(word):
                continue

            senses = entry.get("senses", [])
            translations = ";".join(
                sense.get("glosses", [""])[0] for sense in senses if sense.get("glosses")
            ) or "unknown"
            translations = clean_translations(translations)

            if translations == "unknown" and not block_data[word]["translations"]:
                continue

            block_data[word]["translations"].add(translations)
            block_data[word]["word_freq"] = word_freq_dict.get(word, 10)
            block_data[word]["block_freq"] = block_freq_dict[word]

    return block_data

def generate_tsv():
    word_freq_dict = load_word_frequencies()
    block_freq_dict = calculate_block_frequencies()
    block_data = aggregate_entries(word_freq_dict, block_freq_dict)
    
    with open("dictionary.tsv", "w", encoding="utf-8", newline="") as tsv_file:
        writer = csv.writer(tsv_file, delimiter="\t")
        writer.writerow(["block", "translations", "word_freq", "block_freq", "overall_freq"])
        
        for block, data in block_data.items():
            translations = ";".join(data["translations"])
            word_freq = data["word_freq"]
            block_freq = data["block_freq"]
            overall_freq = word_freq + block_freq
            
            writer.writerow([block, translations, word_freq, block_freq, overall_freq])

if __name__ == "__main__":
    print("Generating dictionary.tsv with frequencies from kaikki.org Korean dictionary...")
    generate_tsv()
    print("Done! Check dictionary.tsv")
