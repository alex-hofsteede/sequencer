Sequencer
=========

A lightweight library to recognize sequences of items and extend them by
predicting the next elements in the sequence. It works by using sequence
definitions eg. `['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']` to
match the input sequence and convert it to a sequence of integers. It then
looks for patterns in this integer sequence in order to try and extend it.

    ['Mon', 'Wed', 'Fri', 'Mon', 'Wed', 'Fri']
would become:
    [0, 2, 4, 0, 2, 4]
Which we then recognize as a repetition of the subsequence:
    [0, 2, 4]
We can then use this to predict that the next item in the sequence will be
    'Mon'

Sequencer can detect more complex types of sequences. It detects ascending or descending
sequences like: `[0, 2, 4, 6, 8]` or `[10, 9, 8, 7, 6]` as well as sequences
that have a geometric ratio like `[2, 4, 8, 16, 32]` or `[1, -1, 1 -1]`



