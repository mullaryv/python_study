# coin is being thrown 30 times;
# The number of trials is provided by the user.
# The goal is to see how much faces were in each trial
# -- it should be very close to standard Bernoulli distribution.

import random

TRIALS = int(input ('number of trials: '))
THROWS = 30

# an array index will mean number of faces in all trials
arr = [0 for i in range (THROWS+1)]
  
# simulate the test, i.e. throw the coin 30 times in each of the TRIALS trials.
for i in range(TRIALS):
  faces = 0
  for j in range (THROWS):
    faces += random.randint(0,1)
  arr[faces] += 1

print(arr)

# print out, replacing each 10 counts with "*"
for i in range(THROWS+1):
  stars = round (arr[i] / 10)
  for j in range (stars):
    print ('*', end='')
  print('\n')


input("press any key")
