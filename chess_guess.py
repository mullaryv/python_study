'''
Chess board with random number of marbles on it, no more than one in each square.
One square is "selected", i.e. it is shown to a person, who can then 
  a) add 1 marble to any empty square
  b) remove a marble from any square
  c) do nothing
After that, another person with no prev. knowledge of a board
should tell which square was selected.
(Two persons above may communicate before the board configuration is created)
'''

# validate individual square
def isValid (square) :
  return (len(square) == 2) and \
         (ord(square[0]) in range (ord('A'), ord('I'))) and \
         (int(square[1]) in range(1,9))

# convert a valid 2-char square to a 6-bit presentation (integer, actually)
def to6bits (square) :
  return (ord(square[0])-ord('A'))*8 + int(square[1])-1

# converts 6-bit (integer) representation to a 2-char square  
def toSquare (bit6) :
  return chr ((bit6>>3) + ord('A')) + str (bit6 % 8 + 1)

# XOR sum of all valid elements in the list
def XORsum (lst) :
  s = 0
  for square in lst:
    if (isValid (square)):
      sq_bit = to6bits(square)
      s = s ^ sq_bit
  return s

  
# read chess board configuration
board = "a2 a4 b7 c8 f3 g3 h5 h6"
# some corner cases: [b1,f6] (b1 selected); [f6] (a1); [c5] (c5)

# process board configuration: convert to upper string, validate
board_lst = board.upper().split()
for square in (board_lst):
  if not isValid(square):
    print ('invalid chess square entry: ', square)
    exit (-10)

board_sum = XORsum (board_lst)  #XOR sum of all marbles

# debug: 6-bits representation of a board
#marbles = list (map (to6bits, board_lst)) 
#print ("integer presentation: ", marbles, "  sum: ", board_sum)

# read and validate "selected" square
sel_inp = input ('Choose a square: ')
sel_str = sel_inp.upper()
if not isValid(sel_str):
  print ('invalid  square: ', sel_inp)
  exit (-20)
  
sel_bits = to6bits (sel_str)
board_sum_plus = board_sum ^ sel_bits
new_square= toSquare (board_sum_plus)

print ("\n  selected: " + sel_str + "  (" + str(sel_bits) + ")")
print ("  board XOR updated: " + str (board_sum_plus))
print ("  square to change: " + new_square)

# If there already exists a marble on the new square in the original board,
# then we should remove it, instead of adding.
# Also special case is when we don't want to change anything on the board
#   (which is the same as putting/removing a marble to/from A1 field)

move = "     (.)" # by default, do nothing
if (new_square in board_lst):
  board_lst[board_lst.index(new_square)] = "  "  #replace (vs. remove), for nice printing
  move = "     (-" + new_square + ")"
else:
  if (board_sum_plus !=0):
    move = "  (+" + new_square + ")"
    board_lst.append (new_square)

print ("original board: " + board + "     (XOR: " + str(board_sum) + ")")
print ("updated board:  " + " ".join (board_lst) + move) 

# check
new_sum = XORsum (board_lst)  #XOR sum of all marbles
print ("\nTEST:  choosen square=" + toSquare (new_sum))
