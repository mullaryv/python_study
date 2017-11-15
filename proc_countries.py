# creates ECL dataset from the countries list
# countries: http://download.geonames.org/export/dump/countryInfo.txt

import sys


#read file name, open file for reading 
if len(sys.argv) < 2:
  print ('  !!!Error: please provide a file name.')
  exit(-1) 

fname = sys.argv[1]
fin = open (fname, 'r')


# list to contain attributes' components
attributes = [];

c = 0
# split input file into distinguished lines, split each line into components
for line in fin:
  #process end of the line symbols
  k = line.find ('\n')
  if k>0:
    line = line[0:k]

  words = line.split('\t')

  print ('{', end="")
  num_words = len (words) 
  for i in range (num_words):
    word = words[i]
    print ('\'' + word + '\'', end="")
    if i < num_words-1:
      print (', ', end="")

  #for word in words:
  #  print ('\'' + word + '\', ', end="")
  print ('},')
'''  
  #create attribute or module name
  attribute = words[0] + '.' + words[1]
  if (words[1] == 'N/A'):
    attribute = '[' + words[0] + ']'

  # add attribute info to the list
  new_lst = [attribute, words[3], words[4].replace('\n', '')]
  #apply filter, if needed
  if (words[3][0:6] == 'Brento' or words[3][0:6] == 'sreeka' or words[1][0:3] == 'N/A'):
    attributes.append(new_lst)
  print ('{', end="")


print (c)   
# close input
fin.close ()  


# Find out the length of the longest attribute name  
max_len = 0
for lst in attributes:
  q_i = len(lst[0])
  if (q_i > max_len):
    max_len = q_i

    
# now format (TODO: most likely there'sa better way, but so far it suffices)
spaces = "                                                              "
format_text = []
for lst in attributes:
  formatted_line = lst[0]
  q_i = len (formatted_line)
  if ((q_i < max_len) and (q_i > 0)):
    formatted_line = lst[0][0:q_i] + spaces[0:max_len-q_i]
    format_text.append([formatted_line, lst[1], lst[2]])


#for line in format_text:
#  print (line)

#sort by user + attribute
list1 = sorted (format_text, key=lambda x: (x[0], x[1]))

  
for lst in list1:
  print (lst[0], lst[1], lst[2])
'''  