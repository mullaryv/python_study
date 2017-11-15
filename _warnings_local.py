import sys

# for formatting purposes (don't know a better way yet)
BLANKS = "                                                               "

C_ATTRIBUTE = 0
C_WCODE     = 1
C_WARNING   = 2

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
    print (FormatField (arr[0], max_len), "    ", arr[1], "    ", arr[2])
  print()    
  return 0



def SortByLargest(item):
  return item[1]

# rolls up and counts by desired field  
def CountsBy (message, by, max_limit = 0) :

  # sort by requested field  
  def srtBy(item):
    return item[by]
  message.sort(key=srtBy)

  size = len (message)
  by_field = list()
  cnt = 0
  current_field = ""
  field = ""

  # roll up by query name
  for arr in message:
    field = arr[by]

    if (current_field == ""):  # in the first run
      current_field = field 
      cnt = 1
      continue

    if (field == current_field):
      cnt = cnt + 1
    else:
      #print (arr[C_WARNING][0:30])
      if (by == C_WCODE):
        by_field.append ([current_field, cnt, arr[C_WARNING][0:30]])
      else:
        by_field.append ([current_field, cnt, ''])
      current_field = field 
      cnt = 1

  # add the last one
  by_field.append ([current_field, cnt, ''])

  by_field.sort(key=SortByLargest, reverse=True)

  res = by_field
  if (max_limit > 0):
    res = [x for x in by_field if (x[1] >= max_limit)]

  return res#by_field
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
  # check if it is a warning
  i_warning = line.find(": warning", 1)
  if (i_warning >= 0):
    #print(line)
    ecl_warn = line.strip()
    components = ecl_warn.split (": ")
    attribute = components[0]
    code = components[1]
    comment = components[2]
    warnings.append ([attribute, code, comment])  # array of components


#for arr in (warnings):
#  print (arr)
#print()  

 
# =================================================================
# ============================= stat  =============================
# =================================================================
'''
  
print ("------------ Warnings per instance of ECL code ------------")
by_ecl = CountsBy (warnings, C_ATTRIBUTE)
PrintStat (by_ecl)
'''


print ("------------ Most frequent warnings ------------")
by_wcode = CountsBy (warnings, C_WCODE)
PrintStat (by_wcode)


print ("------------ Warnings per attribute ------------")
w_attr = list()
for component in (warnings):
  attr = component[C_ATTRIBUTE]
  ind_par = attr.find("(", 1)
  if ind_par > 0:
    component[C_ATTRIBUTE] = attr[0:ind_par] 
    w_attr.append (component)

by_attribute = CountsBy (w_attr, C_ATTRIBUTE, 5)
PrintStat (by_attribute)


'''
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
'''