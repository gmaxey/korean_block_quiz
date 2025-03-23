#!/usr/bin/env python3
import json
import collections
import re

# File paths
INPUT_JSONL = "kaikki.org-dictionary-Korean.jsonl"
OUTPUT_TSV = "dictionary.tsv"

def is_single_block(word):
  return len(word) == 1 and "\uAC00" <= word <= "\uD7A3"

def extract_translations(entry):
  translations = []
  if "senses" in entry:
      for sense in entry["senses"]:
          if "glosses" in sense:
              translations.extend(sense["glosses"])
  return translations

def simplify_translations(translations, word=None):
  cleaned = []
  for t in translations:
      t = t.strip()
      # E1.3.1: Remove "Short for" entries
      if t.lower().startswith("short for"):
          continue
      # E1.3.4: Remove Chinese characters, eumhun readings, parenthetical items, and junk
      # First, remove eumhun reading annotations entirely
      t = re.sub(r'\(eumhun reading.*?\)', '', t)
      # Then, remove any remaining parenthetical items and other junk
      t = re.sub(r'\(.*?\)|[\u4E00-\u9FFF:]+|Alternative form of|More information|\*', '', t)
      # Remove any dangling parentheses and extra whitespace
      t = re.sub(r'[()\[\]]+', '', t).strip()
      # Replace newlines with spaces
      t = t.replace('\n', ' ')
      # Skip if empty or no English
      if not t or not any(c.isascii() for c in t):
          continue
      # Relaxed filtering: Only exclude explicit unwanted terms
      if any(x in t.lower() for x in ["penis", "shit", "bastard"]):
          continue
      cleaned.append(t)
  # E1.3.2: Return None if no valid translations
  if not cleaned:
      return None
  # Debug: Print raw translations for specific words
  if word == "이":
      print(f"Raw translations for 이: {cleaned}")
  # Return a list of cleaned translations (don't join yet)
  return cleaned

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
  single_blocks = collections.defaultdict(list)

  # Process JSONL for single-block words, collecting all translations
  with open(INPUT_JSONL, "r", encoding="utf-8") as f:
      for line in f:
          entry = json.loads(line.strip())
          word = entry.get("word", "")
          if is_single_block(word):
              translations = extract_translations(entry)
              simplified_trans = simplify_translations(translations, word=word)
              if simplified_trans is None:
                  continue
              # Append all translations for this word
              single_blocks[word].extend(simplified_trans)

  # Combine translations and compute frequencies
  combined_blocks = {}
  for word, trans_list in single_blocks.items():
      # Remove duplicates while preserving order
      trans_list = list(dict.fromkeys(trans_list))
      # Combine translations into a single string (max 5 translations to capture more meanings)
      combined_trans = ", ".join(trans_list[:5])
      # Replace any newlines with spaces (just in case)
      combined_trans = combined_trans.replace('\n', ' ')
      word_freq = 1  # Placeholder (could be updated with actual frequency data in the future)
      block_freq = block_freqs.get(word, 0)
      overall_freq = word_freq + block_freq
      combined_blocks[word] = (combined_trans, word_freq, block_freq, overall_freq)

  # E1.5: Sort by overall_freq (descending)
  sorted_blocks = sorted(combined_blocks.items(), key=lambda x: x[1][3], reverse=True)

  # Write to TSV
  with open(OUTPUT_TSV, "w", encoding="utf-8") as f:
      f.write("block\ttranslation\tword_freq\tblock_freq\toverall_freq\n")
      for word, (trans, wf, bf, of) in sorted_blocks:
          # Ensure the line is written as a single line
          f.write(f"{word}\t{trans}\t{wf}\t{bf}\t{of}\n")

  print(f"Generated {OUTPUT_TSV} with {len(sorted_blocks)} entries")

if __name__ == "__main__":
  main()