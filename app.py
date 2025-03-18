import os
import json
import re
from flask import Flask, render_template, jsonify, request
from process_words import get_korean_words_with_freq
import random

app = Flask(__name__)

def load_translations():
    translations = {}
    used_translations = set()  # Track used translations to avoid duplicates
    jsonl_file = 'kaikki-korean-words.jsonl'
    if os.path.exists(jsonl_file):
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line.strip())
                word = entry.get('word')
                senses = entry.get('senses', [])
                if word and len(word) == 1 and all(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in word):
                    for sense in senses:
                        glosses = sense.get('glosses', [])
                        if glosses:
                            gloss = glosses[0]
                            skip_patterns = [
                                "More information", "reading:", "Synonym of", "Root of", 
                                "Infinitive", "conjugative", "plural", "See also", "Alternative",
                                "Substantive", "Short for", "Used to", "form of", "determiner",
                                "surname", "count", "Gangwon", "忙", "薨", "to ", "of "
                            ]
                            if (any(pattern in gloss for pattern in skip_patterns) or 
                                not any(c.isalpha() for c in gloss) or 
                                len(gloss.split()) > 2):
                                continue
                            match = re.search(r'“([^”]+)”|([a-zA-Z]+(?: [a-zA-Z]+)?)', gloss)
                            if match:
                                translation = match.group(1) or match.group(2)
                                # Remove "to " prefix if present
                                translation = translation.replace("to ", "").strip()
                                if (translation and 
                                    all(ord(c) >= 32 and ord(c) <= 126 for c in translation) and  # ASCII only
                                    len(translation) >= 2 and  # Minimum length for clarity
                                    len(translation.split()) <= 2 and 
                                    translation not in used_translations and 
                                    not any(p.lower() in translation.lower() for p in skip_patterns)):
                                    translations[word] = translation
                                    used_translations.add(translation)
                                    break
                            elif any(c.isalpha() for c in gloss):
                                cleaned = re.split(r'[,(]', gloss)[0].strip()
                                cleaned = cleaned.replace("to ", "").strip()
                                if (cleaned and 
                                    all(ord(c) >= 32 and ord(c) <= 126 for c in cleaned) and 
                                    len(cleaned) >= 2 and 
                                    len(cleaned.split()) <= 2 and 
                                    cleaned not in used_translations and 
                                    not any(p.lower() in cleaned.lower() for p in skip_patterns)):
                                    translations[word] = cleaned
                                    used_translations.add(cleaned)
                                    break
    # Fallback to hardcoded if JSONL yields too few valid translations
    if len(translations) < 12:
        hardcoded = {
            "사과": "apple", "책": "book", "집": "house", "물": "water", "불": "fire",
            "눈": "eye", "코": "nose", "입": "mouth", "손": "hand", "발": "foot",
            "귀": "ear", "배": "boat", "꽃": "flower", "별": "star", "숲": "forest"
        }
        for word, trans in hardcoded.items():
            if trans not in used_translations:
                translations[word] = trans
                used_translations.add(trans)
    return translations

translations = load_translations()

def load_words():
    word_freq_pairs = get_korean_words_with_freq(fallback_words=list(translations.keys()))
    valid_pairs = [(word, freq) for word, freq in word_freq_pairs if word in translations]
    if not valid_pairs:
        return [], []
    words, freqs = zip(*valid_pairs)
    return list(words), list(freqs)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cards', methods=['GET'])
def get_cards():
    words, freqs = load_words()
    if not words:
        return jsonify({'korean': [], 'english': [], 'shuffled_english': []})
    
    # Limit to 12 unique pairs
    num_pairs = min(12, len(words))
    if len(words) <= num_pairs:
        selected_words = list(words)
    else:
        unique_words = random.sample(words, k=num_pairs)
        selected_words = unique_words[:num_pairs]
    
    # Ordered translations (for reveal)
    ordered_english = [translations[word] for word in selected_words]
    # Shuffled translations (for initial display)
    shuffled_english = ordered_english.copy()
    random.shuffle(shuffled_english)
    
    return jsonify({
        'korean': selected_words,
        'ordered_english': ordered_english,
        'shuffled_english': shuffled_english
    })

@app.route('/api/check_pair', methods=['POST'])
def check_pair():
    data = request.get_json()
    korean = data['korean']
    english = data['english']
    correct = translations.get(korean) == english
    return jsonify({'correct': correct})

if __name__ == '__main__':
    if not os.path.exists('single_block_freq.txt'):
        from process_words import process_words
        process_words()
    app.run(host='0.0.0.0', port=5000)
