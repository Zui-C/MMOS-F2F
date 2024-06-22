
This repository is an attempt by the MMOS method on automatic theorem proving tasks.

[MMOS Method](https://github.com/cyzhh/MMOS?tab=readme-ov-file) mainly focuses on sampling augmented datasets from open-source models, attempting to find corresponding minimum optimal sets. In automatic theorem proving tasks, the goal of the model is to predict the next tactic based on the current state.

The ATG task was experimentally conducted using [llemma_formal2formal
](https://github.com/wellecks/llemma_formal2formal). 



Comparison of tactic sample accuracy (TSA) and overall accuracy (OA) on MiniF2F datasets.

It is worth noting that overall accuracy is strongly related to the search method used. Here, we use best first search with 32 actions, 100 items limit, and a 20-minute time limit.

| Model                  | TSA  | OA   |
|------------------------|------|------|
| Llemma-7B              | 22.0 | 27.8 |
| Llemma-34B             | 23.2 | 27.5 |
| DeepSeekMath-7B        | 29.4 | 27.8 |
| MMOS-Llemma-7B         | 32.5 | 29.1 |
| MMOS-Llemma-34B        | 30.8 | 28.7 |
| MMOS-DeepSeekMath-7B   | 32.7 | 28.3 |


## Code
`infer.py` is used for test SFT model.

`few_shot.py` is used for test base model.

`proofsearch` is used for early stop. 

training data is in `samples`.
