import MeCab
import re
from collections import Counter

def process_words():
    with open('korean.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    mecab_tagger = MeCab.Tagger()
    parsed = mecab_tagger.parse(text)
    words = [line.split('\t')[0] for line in parsed.split('\n') if line and '\t' in line]
    single_blocks = [word for word in words if len(re.sub(r'[^\w\s]', '', word)) == 1]
    freq = Counter(single_blocks)
    with open('single_block_freq.txt', 'w', encoding='utf-8') as file:
        for word, count in freq.items():
            file.write(f"{word}\t{count}\n")

def get_korean_words():
    if not os.path.exists('single_block_freq.txt'):
        process_words()
    with open('single_block_freq.txt', 'r', encoding='utf-8') as file:
        return [line.split('\t')[0] for line in file if line.strip()]

if __name__ == '__main__':
    process_words()
