# converts decimal to a binary using remainder as each preceeding bit

d = int (input ('number: '))

binstr = ''
if (d == 0) : binstr = '0'


# main cycle
while (d > 0):
  q = d % 2
  binstr = str(q) + binstr
  #print ("%5d%8d%12s" % (d, q, binstr))
  d //= 2

print (binstr)

input("press any key")
