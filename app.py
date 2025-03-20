#!/usr/bin/env python3
import os
import csv
import random
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

def load_dictionary(file_path="dictionary.tsv"):
    translations = {}
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            block = row["block"]
            trans = row["translation"]  # Fixed from "translations"
            if not trans.strip():
                continue
            translations[block] = {
                "translation": trans,
                "overall_freq": float(row["overall_freq"])
            }
    return translations

translations = load_dictionary()

def get_quiz_blocks(slice_num=0, num_pairs=12):
    sorted_blocks = sorted(translations.items(), key=lambda x: x[1]["overall_freq"], reverse=True)
    total_blocks = len(sorted_blocks)
    slice_size = total_blocks // 10
    start = slice_num * slice_size
    end = start + slice_size if slice_num < 9 else total_blocks
    
    candidates = sorted_blocks[start:end]
    if not candidates:
        return []
    return random.sample(candidates, min(num_pairs, len(candidates)))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cards', methods=['GET'])
def get_cards():
    slice_num = int(request.args.get('slice', 0))
    blocks_data = get_quiz_blocks(slice_num)
    if not blocks_data:
        return jsonify({'korean': [], 'english': [], 'shuffled_english': []})
    
    selected_words, selected_data = zip(*blocks_data)
    ordered_english = [data["translation"] for data in selected_data]
    shuffled_english = ordered_english.copy()
    random.shuffle(shuffled_english)
    
    return jsonify({
        'korean': list(selected_words),
        'ordered_english': ordered_english,
        'shuffled_english': shuffled_english
    })

@app.route('/api/check_pair', methods=['POST'])
def check_pair():
    data = request.get_json()
    korean = data['korean']
    english = data['english']
    correct = english == translations.get(korean, {}).get("translation", "")
    return jsonify({'correct': correct})

if __name__ == '__main__':
    if not os.path.exists("dictionary.tsv"):
        print("Error: dictionary.tsv not found. Please generate it first.")
    else:
        app.run(host='0.0.0.0', port=5000)