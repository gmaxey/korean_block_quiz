from flask import Flask, render_template, request
import random
import os
from process_words import *  # Import to generate single_block_freq.txt if needed

app = Flask(__name__)

# Ensure single_block_freq.txt exists
if not os.path.exists('single_block_freq.txt'):
    os.system('python3 process_words.py')

# Load single-block words
with open('single_block_freq.txt', 'r', encoding='utf-8') as f:
    blocks = [line.split(':')[0] for line in f]

meanings = {
    '신': 'new / to wear (feet)',
    '양': 'sheep / quantity',
    '발': 'foot',
    '말': 'horse / speech',
    '책': 'book',
    '상': 'table / prize'
}

@app.route('/')
def index():
    word = random.choice(blocks)
    correct_meaning = meanings.get(word, "Unknown")
    wrong_options = random.sample([v for k, v in meanings.items() if k != word], 3)
    options = wrong_options + [correct_meaning]
    random.shuffle(options)
    return render_template('index.html', word=word, options=options, correct=correct_meaning)

@app.route('/check', methods=['POST'])
def check():
    user_answer = request.form['answer']
    correct_answer = request.form['correct']
    result = "Correct!" if user_answer == correct_answer else f"Wrong! Correct answer: {correct_answer}"
    return render_template('index.html', word=request.form['word'], options=request.form.getlist('options'), 
                           correct=correct_answer, result=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
