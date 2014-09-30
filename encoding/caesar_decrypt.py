# Most primitive Caesar de-cypher

# Read message to encode:
#msg = str (input ('enter lower case string: '))
fin = open ("secret.encoded", "r")
msg = fin.read()
fin.close()

dist = int (input ('distance: '))

# decode only characters from the interval:
MIN_CH = 32
MAX_CH = 128

# all calculations are by modulo 96 (base ASCII table minus special symbols)
max_dist = MAX_CH - MIN_CH
if (dist >= max_dist):
  dist %= max_dist

msg_len = len (msg)

# this will contain de-cyphered text
plain_txt=""

# replace each character in the input string to corresponding cypher value
for i in range(msg_len):
  chOrd = ord(msg[i])

  # if the character is outside of allowed interval, don't encode it
  if (chOrd > MAX_CH) or (chOrd < MIN_CH):
    newOrd = chOrd
  else:
    newOrd = chOrd - dist;
    if (newOrd < MIN_CH):
      newOrd = max_dist + chOrd - dist
  plain_txt += chr(newOrd)

print (plain_txt)
