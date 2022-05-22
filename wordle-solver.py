import pandas as pd
import numpy as np
import string
from collections import defaultdict
import math
import argparse

p = argparse.ArgumentParser()
p.add_argument('-v', action='store_true')
p.add_argument('-a', action='store_true')
args = p.parse_args()
verbose = args.v

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
new_rows = []
for w in allowed_words[0]:
    if w not in counted_words:
        new_row = {'word': w, 'count':0, 'freq':0}
        new_rows.append(new_row)

words = words.append(pd.DataFrame(new_rows))
        
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
    # Have to keep track of position of green chars
    green_idx = defaultdict(list)
    grey = set()
    for i, r in enumerate(result):
        char = word[i]
        if r == 'grey':
            grey.add(char)
        elif r == 'green':
            green_idx[char].append(i)
    green_and_grey = set(green_idx.keys()).intersection(grey)
    for i, r in enumerate(result):
        char = word[i]
        if r == 'green':
            a[i] = set([char])
        elif r == 'yellow':
            try:
                a[i].remove(char)
            except:
                continue
            b.add(char)
        elif r == 'grey':
            if char in green_and_grey:
                # Remove this option from all but the green positions
                for i, pos in enumerate(a):
                    if i in green_idx[char]:
                        continue
                    try:
                        pos.remove(char)
                    except:
                        continue
            else:
                # Remove from all positions
                for pos in a:
                    try:
                        pos.remove(char)
                    except:
                        continue

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

def find_clues_solutions(a, b, guess_num, verbose=False):
    ok_words = find_ok_words(a, b)
    
    print()
    print(len(ok_words), 'valid words.')
    
    # Get the most common word in ok_words
    most_common_words = words[words['word'].isin(ok_words)]
    most_common_words.index = most_common_words['word']
    most_common_words = most_common_words[['freq']]
    most_common_words.columns = ['Word Frequency']
    most_common_words.index.name = None
        
    best_info_words = best_words.loc[ok_words][['avg']]
    best_info_words.columns = ['Information Gain']
        
    best_of_both = best_info_words.join(most_common_words)
    
#     if guess_num < 2:
#         print('\nRecommended word (best information gain):')
#         print(best_info_words.index[0])
#     elif guess_num < 5:
#         print('\nRecommended word (best combination of information gain and word frequency):')
#         print(best_of_both.index[0])
#     else:
#         print('\nRecommended word (most common word matching constraints):')
#         print(most_common_words.index[0])

    # New way: take a weighted average of the rank of each
    best_of_both['word'] = best_of_both.index
    best_of_both = best_of_both.sort_values(['Information Gain']).reset_index().drop(['index'],axis=1)
    best_of_both['info_idx'] = best_of_both.index
    best_of_both = best_of_both.sort_values(['Word Frequency']).reset_index().drop(['index'],axis=1)
    best_of_both['freq_idx'] = best_of_both.index
    best_of_both.index = best_of_both['word']

    freq_weight = 0.2 * guess_num
    info_weight = 1 - freq_weight
    
    best_of_both['Combined Score'] = best_of_both['info_idx']*info_weight + best_of_both['freq_idx']*freq_weight
    best_of_both = best_of_both.sort_values(['Combined Score'], ascending=False)
    
    if verbose == True:
        print('\nFrequent letters in common positions):')
        print(best_info_words.head())
        print('\nMost common words:')
        print(most_common_words.head())
        print(f'\nWeighted combination (w_info={info_weight}, w_freq={freq_weight}):')
        print(best_of_both[['Combined Score', 'Information Gain', 'Word Frequency']].head(5))
        
    print('\nRecommended word:')
    print(best_of_both.index[0])
    print()
    return best_of_both.index[0]
    
# Shorthands to make entering results easier
sh = ['grey', 'yellow', 'green']

while True:
    # Allowed letters
    a = [set(az) for _ in range(5)]
    # Necessary letters
    b = set()
    
    quit = False
    print('\n=============\n')
    print('\nWORDLE SOLVER')
    word = find_clues_solutions(a, b, 0, verbose=verbose)
    print()
    for i in range(1, 7):
        if not args.a:
            word = input(f'Guess {i} (or type "exit", "restart"): ')
        else:
            print(f"Enter the word ({word}) in Wordle now.")
        if word == 'restart':
            break
        elif word == 'exit':
            quit = True
            break
        result = input('Result? (0=grey, 1=yellow, 2=green): ')
        result = [sh[int(s)] for s in result]
        use_clues(word, result)
#         print('Best solution word is:', find_solution(a, b))
#         print('Best clue word is:', find_clue(a,b))
        try:
            word = find_clues_solutions(a, b, i, verbose=verbose)
        except:
            print('Impossible! Restarting.')
            break
        print('')
        
    if quit:
        break