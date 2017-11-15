import sys
import operator

DEBUG = False

# for formatting purposes (don't know a better way yet)
BLANKS = "                                                               "

C_QUERY     = 0
C_ATTRIBUTE = 1
C_WCODE     = 2
C_WARNING   = 3

OUTPUT_LIMIT = 100     # output limit


# finds the longest value in a specified field in the list
def FieldMaxLength (lst, by):
  max_len = 0
  for arr in lst:
    current_len = len (arr[by])
    if (current_len > max_len):
      max_len = current_len
  return max_len


#returns a string padded with trailing spaces up to certain length  
def FormatField (fd, max_len):
  diff = max_len - len (fd)
  if diff <=0: return fd
  return fd + BLANKS[0:diff]
  

# prints a formatted stat  
def PrintStat (in_lst):
  num = len(in_lst)
  if num > OUTPUT_LIMIT:
    num = OUTPUT_LIMIT

  lst = in_lst[0:num]
  max_len = FieldMaxLength (lst, 0)
  for arr in lst:
    #TODO: add arr[3]
    print (FormatField (arr[0], max_len), "    ", arr[1], "    ", arr[2])
  print()    
  return 0



def SortByLargest(item):
  return item[1]


# rolls up and counts by desired field  
def CountsBy (message, by, by2=100) :

  # sort by requested field  
  def srtBy(item):
    return item[by]
  message.sort(key=srtBy)
  if (by2 != 100):
    message.sort(key = operator.itemgetter(by, by2))

  if (DEBUG):
    for arr in (message): print (arr)


  size = len (message)
  by_field = list()
  
  cnt = 0
  m = message[0]
  warn =  m[C_WARNING]
  current_field = m[by]
  current_field2 = ''
  if (by2 != 100): current_field2 = m[by2]

  # roll up by query name
  for arr in message:
    field = arr[by]
    field2 = ''
    if (by2 != 100): field2 = arr[by2]

    #if (DEBUG): print (arr)
    if (DEBUG): print (field + ' ==? ' + current_field + '  :  ' + field2 + ' ==? ' + current_field2)

    is_same = (field == current_field) and (field2 == current_field2)
    if (DEBUG): print (is_same)

    #if (field == current_field):
    if (is_same):
      cnt = cnt + 1
    else:
      if (DEBUG): print ('--- record')
      if (by == C_WCODE):
        by_field.append ([current_field, cnt, warn])
      else:
        if (by == C_ATTRIBUTE):
          if (by2 != 100):
            by_field.append ([current_field, cnt, current_field2, warn])
          else:
            by_field.append ([current_field, cnt, warn])
        else:
          by_field.append ([current_field, cnt, ''])
      current_field = field 
      cnt = 1
      warn = arr[C_WARNING]
      current_field2 = field2
      #if (by2 != 100): current_field2 = m[by2]

    if (DEBUG): print ('cnt: ', cnt)
    if (DEBUG): print ('current_field: ', current_field)
    if (DEBUG): print ('current_field2: ', current_field2)

  # add the last one
  if (by == C_WCODE):
    by_field.append ([current_field, cnt, warn])
  else:
    if (by == C_ATTRIBUTE):
      by_field.append ([current_field, cnt, warn])
    else:
      by_field.append ([current_field, cnt, '.'])

  by_field.sort(key=SortByLargest, reverse=True)

  return by_field
# def CountsBy ----------------------------------------
  
  

#read name of the file containing warnings, open a file for reading
if len(sys.argv) < 2:
  print ('needs a name of the logfile')
  exit(-1) 

fname = sys.argv[1]
fin = open (fname, 'r')



# go through each line, ignoring non-relevant ones
warnings = list()  #to keep all the warnings along with a query name
query_name = "";

for line in fin:
  #print (line)
  # check if new query begins here
  i_query = line.find("Processing ", 0)
  if (i_query >= 0):
    query_name = line[i_query+11:].strip()
    #print (query_name)

  # check if it is a warning
  # i_eclserver = line.find("eclserver: ", 1)
  i_eclserver = line.find("eclcc: ", 0)
  if (i_eclserver >= 0):
    ecl_warn = line.strip()
    components = ecl_warn.split (": ")
    attribute = components[1]

    # clean attribute name
    i_commit = attribute.find("}/", 0)
    if (i_commit > 0):
      attribute = attribute[i_commit+2:]
    i_par = attribute.find("(", 0)
    if (i_par > 0):
      attribute = attribute[0:i_par]

    code = components[2]
    comment = components[3]
    if (len (components) > 4):
      comment = components[3] + components[4]
    comment = FormatField (comment, 60)
    warnings.append ([query_name, attribute, code, comment])  # array of components


#for arr in (warnings):
#  print (arr)
#print()  

 
# =================================================================
# ============================= stat  =============================
# =================================================================
print ("------------ Warnings per query ------------")
by_query = CountsBy (warnings, C_QUERY)
PrintStat (by_query)


print ("------------ Warnings per attribute ------------")
by_attribute = CountsBy (warnings, C_ATTRIBUTE)
PrintStat (by_attribute)


print ("------------ Most frequent warnings ------------")
by_wcode = CountsBy (warnings, C_WCODE)
PrintStat (by_wcode)


print ("------------ Most frequent instance of a warning in ECL file ------------")
by_ecl = CountsBy (warnings, C_ATTRIBUTE, C_WCODE)
PrintStat (by_ecl)


print ("------------ Indices causing most warnings ------------")
w_index = list()
for component in (warnings):
  attr = component[C_WARNING]
  ind_tilda = attr.find("~", 1)
  if (ind_tilda > 0):
    component[C_WARNING] = attr[ind_tilda:]
    w_index.append (component)

by_index = CountsBy (w_index, C_WARNING)
PrintStat (by_index)


#printStat (w_index)


#mlen = FieldMaxLength(warnings, C_QUERY)
#print (mlen)
#print ("[", FormatField ("asdfg", mlen), "]")
#print (FormatField ("asdfg", mlen),"]")
