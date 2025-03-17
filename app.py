import os
from flask import Flask, render_template, jsonify, request
from process_words import get_korean_words  # Existing function to load words
import random

app = Flask(__name__)

# Hardcoded translations (expand this as needed)
translations = {
    "사과": "apple",
    "책": "book",
    "집": "house",
    "고양이": "cat",
    "강아지": "dog",
    "나무": "tree",
    "물": "water",
    "하늘": "sky",
    "태양": "sun",
    "달": "moon"
}

def load_words():
    # Load Korean words from single_block_freq.txt
    korean_words = get_korean_words()
    # Filter to only include words with translations
    return [word for word in korean_words if word in translations]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cards', methods=['GET'])
def get_cards():
    words = load_words()
    # Select 5 random words
    selected_words = random.sample(words, min(5, len(words)))
    translations_list = [translations[word] for word in selected_words]
    # Randomize the order of translations
    random.shuffle(translations_list)
    return jsonify({
        'korean': selected_words,
        'english': translations_list
    })

@app.route('/api/check_pair', methods=['POST'])
def check_pair():
    data = request.get_json()
    korean = data['korean']
    english = data['english']
    # Check if the pair is correct
    correct = translations.get(korean) == english
    return jsonify({'correct': correct})

if __name__ == '__main__':
    if not os.path.exists('single_block_freq.txt'):
        # Generate the file if it doesn't exist (from your existing logic)
        from process_words import process_words
        process_words()
    app.run(host='0.0.0.0', port=5000, debug=True)
