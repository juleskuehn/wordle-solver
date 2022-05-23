# wordle-solver

A logic-based [Wordle](https://www.nytimes.com/games/wordle/index.html) solver based on my intuition about what makes a "good" guess.

For more information see `wordle-explore.ipynb`.

## Online usage
Try it in your browser using the link below:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/juleskuehn/wordle-solver/HEAD)

Open `wordle-explore.ipynb` then click the play button.

## CLI usage
* `pip install pandas numpy`
* `python wordle-solver.py`
 
### Flags
`-a`: Auto mode. Assumes you always accept the suggestion.
`-v`: Verbose. Shows top 5 guess options and their scores.