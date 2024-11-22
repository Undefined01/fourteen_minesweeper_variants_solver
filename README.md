# 14 Minesweeper Variants 2 Solver

14 Minesweeper Variants 2 is a minesweeper game published on Steam with 14 different rule sets. This project is a solver for the game. Besize, it contains a program to recognize the game board, solve the puzzles, and play the game automatically.

Supported rule sets:
- [x] Vanilla: Classic minesweeper rules, clues indicates the number of mines in the 3x3 area centered on the cell
- [x] Horizontal: Each mine has a horizontal adjacent mine.
- [x] Connected: Each orthogonally connected mine region is a rectangle, and all mine regions are diagonally connected.
- [x] Segment: Each row contains one consecutive segment of mines
- [x] Group: Each continuous mine region is of size 4
- [x] Flower: Each mine in a colored cell has exactly one mine in the orthogonally adjacent cell.
- [x] Bridge: there are two
- [x] Triple: Each triple of cells contains exactly one mine
- [ ] Cross
- [x] Deviation: Clues indicate the number of mines in the 3x3 area centered on the cell above.
- [ ] Multiply
- [x] Encrypted: The clues are encoded by letters. Each letter corresponds to a number, and each number corresponds to a letter.
- [x] Modulo: The clues are the number of mines in the 3x3 area centered on the cell modulo 3.
- [ ] Area
- [x] Liar: The clues are the number of mines in the 3x3 area centered on the cell, but some clues are wrong, namely the liars. Liar is one greater or one less than the actual value. Each row and each column has exactly one liar.
- [ ] Combined
- []