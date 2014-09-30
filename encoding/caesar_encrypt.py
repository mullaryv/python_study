# Most primitive Caesar cypher

fin = open ("secret.original", "r")
msg = fin.read()
fin.close()

dist = int (input ('distance: '))

# encode only characters from the interval:
MIN_CH = 32
MAX_CH = 128

# all calculations are by modulo 96 (base ASCII table minus special symbols)
max_dist=MAX_CH - MIN_CH
if (dist >= max_dist):
  dist %= max_dist
  
msg_len = len (msg)

# this is the cyphered text
code=""

# replace each character in the input string to corresponding cypher value
for i in range(msg_len):
  chOrd = ord(msg[i])
  # if the character is outside of allowed interval, don't encode it
  if (chOrd > MAX_CH) or (chOrd < MIN_CH):
    newOrd = chOrd
  else:
    newOrd = chOrd + dist
    if (newOrd > MAX_CH):
      newOrd = MIN_CH + newOrd - MAX_CH
  code += chr(newOrd)

print (code)  
fout = open ("secret.encoded", "w")  
fout.write(code)
fout.close()
