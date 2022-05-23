# wordle-solver

A logic-based [Wordle](https://www.nytimes.com/games/wordle/index.html) solver based on my intuition about what makes a "good" guess.

For more information see `wordle-explore.ipynb`.

## Usage
Try it in-browser using the link below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/juleskuehn/wordle-solver/HEAD)

Open `wordle-explore.ipynb` then select Run > Run All Cells from the menu. This will display recommended words.

Open Wordle in a new browser window. Type your guess into Wordle and the solver. Then, type the result from Wordle into the solver.

New recommended words will be displayed.

## CLI usage
* `pip install pandas numpy`
* `python wordle-solver.py`
 
### Flags
`-a`: Auto mode. Assumes you always accept the suggestion.

`-v`: Verbose. Shows top 5 guess options and their scores.
