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

import math
from functools import reduce

# validate individual square, should be from ['A1',...'H8']
def isValid (square) :
  return (len(square) == 2) and \
         (ord(square[0]) in range (ord('A'), ord('I'))) and \
         (int(square[1]) in range(1,9))


# convert a valid 2-char square to an ordinal from [A1=1,A2=9,...H8=64]
def toOrdinal (square) :
  return (ord(square[0])-ord('A') +1) + (int(square[1])-1)*8


# converts an ordinal (integer) to a 2-char square name
def toSquare (ordinal) :
  n = ordinal - 1
  num = 1 + math.floor (n/8)
  let = chr(ord ('A') + n%8)
  return let + str(num)


# sum of all numbered squares in the list
def sum64 (lst) :
  s = 0
  for square in lst:
    s += toOrdinal(square)
  return s
  
  
# read chess board configuration
board = "a2 a4 b7 c8 f3 g3 h5 h6"
#board = "c5"
# some corner cases: [b1,f6] (b1 selected); [f6] (a1); [c5] (c5)

# process board configuration: convert to upper string, validate
board_lst = board.upper().split()
for square in (board_lst):
  if not isValid(square):
    print ('invalid chess square entry: ', square)
    exit (-10)

board_sum = sum64 (board_lst)  #direct sum all occupied squares
#print (board_sum)

#representation of a board as a collection of natural numbers
marbles = list (map (toOrdinal, board_lst)) 

# read and validate "selected" square
sel_inp = input ('Choose a square: ')
sel_str = sel_inp.upper()
if not isValid(sel_str):
  print ('invalid  square: ', sel_inp)
  exit (-20)
  
sel_square = toOrdinal (sel_str)  #ordinal number of selected square

sub_board = 2080 - board_sum
#rem = sub_board - math.floor (sub_board / 64)*64
rem = math.floor (sub_board % 64)

print ("\n  initial board: ", board_lst, "  selected = " + sel_str + " (" + str(sel_square) + ")")
print ("  numbered board: ", marbles, "  (sum:", board_sum, "  remainder:", rem, ")")

#print ("\n  selected: " + sel_str + "  (" + str(sel_square) + ")")

# we can either add or remove a marble (both numbers are from [1..64])
num_add = int (math.fabs(rem - sel_square))
num_remove = 64 - num_add
if (sel_square > rem):  #swap
  t = num_remove
  num_remove = num_add
  num_add = t  
print ("    candidates to add/remove: [" + str(num_add) + "," + str (num_remove) + "]")
  

#modify board, if needed
done = False

if (sel_square == rem): #nothing to do  
  print ("    no need to modify")
  done = True
# else try to modify board
else:
  if num_add not in (marbles):           #add
    marbles.append (num_add)
    print ("    added:" + str(num_add) +" (" + toSquare (num_add) + ")")
    done = True
  else:                                  #remove
    if num_remove in (marbles):
      marbles.remove (num_remove)
      print ("    removed:" + str(num_remove) +" (" + toSquare (num_remove) + ")")
      done = True

if done:
  print ("  modified board: " + str (marbles))
#  print ("              or: " + str (marbles))
else:
  print ("  !error: cannot do anything: ", num_1, ", ", num2)
  exit (-100)
  

# check
new_sub_board = 2080 - reduce(lambda x, y: x+y, marbles)  #direct sum of all numbered squares in modified list
rem_test = math.floor (new_sub_board % 64)
print ("\nTEST:  board: " + str (marbles), "  (sum:", new_sub_board, ", remainder:", rem_test,")")
print ("TEST:    selected " + sel_str + " == " + toSquare (rem_test) + " --> " + str(sel_str==toSquare (rem_test)))


        
