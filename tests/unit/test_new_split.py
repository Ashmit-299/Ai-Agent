import re

script = '''Title: Introduction to Linear Regression
Welcome to this short lesson on linear regression.
In this video, we'll cover:
1) What is linear regression?
2) The simple linear model y = mx + b.
Thank you for watching — try implementing a simple regression now!'''

# New splitting logic
lines = script.split('\n')
sentences = []
for line in lines:
    line = line.strip()
    if line:
        line_sentences = re.split(r'[.!?]', line)
        for sent in line_sentences:
            sent = sent.strip()
            if sent:
                sentences.append(sent)

print('New sentence splitting:')
for i, sentence in enumerate(sentences, 1):
    print(f'Frame {i}: {repr(sentence)}')
print(f'Total frames: {len(sentences)}')