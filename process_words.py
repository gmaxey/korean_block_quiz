from wordfreq import word_frequency
import MeCab
import os

mecab_tagger = MeCab.Tagger()

if not os.path.exists('single_block_freq.txt'):
    with open('korean_words.txt', 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f]

    block_freq = {}
    for word in words:
        blocks = [word[i:i+1] for i in range(len(word))]
        for block in blocks:
            freq = word_frequency(block, 'ko')
            block_freq[block] = block_freq.get(block, 0) + freq + 1

    sorted_blocks = sorted(block_freq.items(), key=lambda x: x[1], reverse=True)
    with open('single_block_freq.txt', 'w', encoding='utf-8') as f:
        for block, freq in sorted_blocks[:50]:
            f.write(f"{block}: {freq}\n")
