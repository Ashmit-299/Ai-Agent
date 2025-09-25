import re

# Test script content
script = '''Title: Introduction to Linear Regression
Welcome to this short lesson on linear regression.
In this video, we'll cover:
1) What is linear regression?
2) The simple linear model y = mx + b.
Thank you for watching — try implementing a simple regression now!'''

print('Original script:')
print(repr(script))
print()

# Test sentence splitting with current regex
sentences = re.split(r'(?<=[.!?])\s+', script)
sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

print('Split sentences with current regex:')
for i, sentence in enumerate(sentences, 1):
    print(f'Frame {i}: {repr(sentence)}')
print(f'Total frames: {len(sentences)}')
print()

# Test with simpler approach - split by periods, exclamation, question marks
sentences2 = re.split(r'[.!?]', script)
sentences2 = [s.strip() for s in sentences2 if s.strip()]

print('Split sentences with simple regex:')
for i, sentence in enumerate(sentences2, 1):
    print(f'Frame {i}: {repr(sentence)}')
print(f'Total frames: {len(sentences2)}')