# wordle-solver

A logic-based, "hard mode" [Wordle](https://www.nytimes.com/games/wordle/index.html) solver based on my intuition about what makes a good guess.

<img width="600" alt="wordle-solver" src="https://user-images.githubusercontent.com/1150048/172744063-fc360bd5-5a44-49bd-86c0-989b4803bd2c.png">

## Usage
Try it in-browser using the link below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/juleskuehn/wordle-solver/HEAD?labpath=wordle-explore.ipynb)

Select Run > Run All Cells from the menu. After a few moments, the focus will move to an interactive prompt which displays recommended words.

For testing it out, I recommend opening [Wordle Unlimited](https://wordleunlimited.org/) in a new browser window. Type your guess into Wordle and the solver. Type the clues from Wordle into the solver. New recommended words will be displayed.

## CLI usage
* `pip install pandas numpy`
* `python wordle-solver.py`
 
### Flags
`-a`: Auto mode. Assumes you always accept the suggestion, so you don't have to type it out.

`-v`: Verbose. Shows top 5 guess options and their scores.
