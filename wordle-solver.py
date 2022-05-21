import pandas as pd
import numpy as np
import string
from collections import defaultdict
import math

print('Preparing vocabulary...')

# https://www.kaggle.com/datasets/rtatman/english-word-frequency?resource=download
words = pd.read_csv('./data/unigram_freq.csv')
az = string.ascii_lowercase

# Filter to 5 letter words
words = words[words['word'].str.len() == 5]
words['freq'] = words['count'] / words['count'].max()

# Allowable wordle words
# https://github.com/tabatkins/wordle-list
allowed_words = pd.read_csv('./data/wordle-allowed-words.txt', header=None)

# Filter word frequency table to include allowed words only
words = words[words['word'].isin(set(allowed_words[0]))]

# Add the other allowed words but with count and freq 0
counted_words = set(words['word'])
for w in allowed_words[0]:
    if w not in counted_words:
        new_row = {'word': w, 'count':0, 'freq':0}
        words = words.append(new_row, ignore_index=True)
        
# Letter frequency
letter_freq = defaultdict(int)
for _, w in words.iterrows():
    for char in w['word']:
#         Many ways to weight this:
#         letter_freq[char] += w['freq']
#         letter_freq[char] += 1
        letter_freq[char] += 1 + math.sqrt(w['freq'])

sorted_letters = sorted(letter_freq.items(), key=lambda x: -x[1])

# Find the best "starting words"
# Best: maximizing total letter_freq (but 0 score for repeated letter)
# This doesn't take into account letter position
word_goodness = defaultdict(float)
for w in allowed_words[0]:
    used_chars = set()
    for char in w:
        if char in used_chars:
            continue
        word_goodness[w] += letter_freq[char]
        used_chars.add(char)
        
sorted_words = sorted(word_goodness.items(), key=lambda x: -x[1])

# Take letter position into account
# Letter frequency per position
letter_pos_freq = [defaultdict(float) for _ in range(5)]
for _, w in words.iterrows():
    for i, char in enumerate(w['word']):
#         Many ways to weight this:
#         letter_freq[char] += w['freq']
#         letter_freq[char] += 1
        letter_pos_freq[i][char] += 1 + math.sqrt(w['freq'])

sorted_pos_letters = [sorted(letter_pos_freq[i].items(), key=lambda x: -x[1]) for i in range(5)]

# Find the best "starting words"
# Best: maximizing total letter_freq (but 0 score for repeated letter)
# This doesn't take into account letter position
word_goodness_pos = defaultdict(float)
for w in allowed_words[0]:
    used_chars = set()
    for i, char in enumerate(w):
#         if char in used_chars:
#             continue
        word_goodness_pos[w] += letter_pos_freq[i][char]
        used_chars.add(char)
        
sorted_words_pos = sorted(word_goodness_pos.items(), key=lambda x: -x[1])

word_good_df = pd.DataFrame(dict(word_goodness), index=['']).T
word_good_df.columns = ['overall']
word_good_df_pos = pd.DataFrame(dict(word_goodness_pos), index=['']).T
word_good_df_pos.columns = ['position']
word_good_df_all = word_good_df.join(word_good_df_pos)
word_good_df_all['avg'] = (
    (word_good_df_all['overall'] / word_good_df_all['overall'].max())
    + (word_good_df_all['position'] / word_good_df_all['position'].max())
) / 2
best_words = word_good_df_all.sort_values(['avg'], ascending=False)

best_word_list = best_words.index
best_word_array = np.array([np.array([c for c in w]) for w in best_word_list])

def use_clues(word, result):
    # Special case: Same letter is green and grey
    green = set()
    grey = set()
    for i, r in enumerate(result):
        char = word[i]
        if r == 'grey':
            grey.add(char)
        elif r == 'green':
            green.add(char)
    green_and_grey = green.intersection(grey)
    for i, r in enumerate(result):
        char = word[i]
        if r == 'grey' and char not in green_and_grey:
            for pos in a:
                try:
                    pos.remove(char)
                except:
                    continue
        elif r == 'yellow':
            try:
                a[i].remove(char)
            except:
                continue
            b.add(char)
        elif r == 'green':
            a[i] = set([char])

# Find all allowable words matching the constraints
def find_ok_words(a, b):
    a_met = (
        np.in1d(best_word_array[:,0], list(a[0]))
        & np.in1d(best_word_array[:,1], list(a[1]))
        & np.in1d(best_word_array[:,2], list(a[2]))
        & np.in1d(best_word_array[:,3], list(a[3]))
        & np.in1d(best_word_array[:,4], list(a[4]))
    )
#     print('meets a:', a_met.sum())
    if len(b) > 0:
        b_met_each = []
        for char in b:
            b_met_each.append(np.array([char in word for word in best_word_list]))
        b_met_all = np.array([True] * len(best_word_list))
        for b_met in b_met_each:
            b_met_all = b_met_all & b_met
    else:
        b_met_all = np.array([True] * len(best_word_list))
#     print('meets b:', b_met_all.sum())
    ok_words = best_word_array[a_met & b_met_all]
    return [''.join(w) for w in ok_words]

# Find the best clue word (most information)
def find_clue(a, b):
    ok_words = find_ok_words(a, b)
    # ok_words is already ranked by how useful the letters are
    return ok_words[0]

# Find the most likely solution word (most common)
def find_solution(a, b):
    ok_words = find_ok_words(a, b)
    print(len(ok_words), 'matching words.')
    # Get the most common word in ok_words
    ok_words_sorted = words[words['word'].isin(ok_words)]
    return ok_words_sorted['word'].values[0]
    
# Shorthands to make entering results easier
sh = ['grey', 'yellow', 'green']

while True:
    # Allowed letters
    a = [set(az) for _ in range(5)]
    # Necessary letters
    b = set()
    
    quit = False

    for i in range(6):
        word = input(f'Guess {i+1} (or type "exit", "restart"): ')
        if word == 'restart':
            break
        elif word == 'exit':
            quit = True
            break
        result = input('Result? (0=grey, 1=yellow, 2=green:\n')
        result = [sh[int(s)] for s in result]
        use_clues(word, result)
        print('Best solution word is:', find_solution(a, b))
        print('Best clue word is:', find_clue(a,b))
        print('========\n')
        
    if quit:
        break