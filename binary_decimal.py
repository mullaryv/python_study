# converts binary (represented by an input string) to a decimal

bin_str = str (input ('string representation of binary: '))

l = len (bin_str)

sum = 0
err=False
for i in range(0, l):
  ch = bin_str[i]
  if (ch == '1'): sum += 2**(l-i-1)
  else:
    if (ch != '0'):
      err = True
      break

if (err):
  print('invalid input string:' + bin_str)
else:
  print(bin_str + '   ' + str(sum))

input("press any key")
