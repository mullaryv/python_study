# formats deployment log into some of a nice view

# define text to replace with acronyms
SUSPENDED_LAYOUT = "is being loaded in suspended state because In index"
SI = "~SI"
SUSPENDED_SUPERKEY = "is being loaded in suspended state because SuperKey"
SSK = "~SK"
SUSPENDED_ROXIEKEY = "is being loaded in suspended state because Roxie server key file"
SRK = "~SR"
SUSPENDED_PACKAGE = "is being loaded in suspended state because PACKAGE_ERROR: Compulsory SuperFile"
SP = "~SP"

# read input log and split it into distinguished lines
fin = open ("_dev.log", 'r')
    # alternatively, I could read it in full and split into lines:
    #text_orig = fin.read()
    #lines = text_orig.split('\n')
    #fin.close ()


# list to contain ameliorated lines
new_text = []

# make each line in the original log shorter: cut out, replace, etc.
line_tmp = ""
for line in fin:
  # cut off everything before the query name
  q_ind = line.find("\"Query ", 1)
  if (q_ind >= 0):
    line_tmp = line[q_ind+7:]

  # replace all known long description with abbreviations
  q_ind = line_tmp.find(SUSPENDED_LAYOUT, 1)
  if (q_ind >= 0):
    line_tmp = line_tmp.replace (SUSPENDED_LAYOUT, SI)

  q_ind = line_tmp.find(SUSPENDED_SUPERKEY, 1)
  if (q_ind >= 0):
    line_tmp = line_tmp.replace (SUSPENDED_SUPERKEY, SSK)

  q_ind = line_tmp.find(SUSPENDED_ROXIEKEY, 1)
  if (q_ind >= 0):
    line_tmp = line_tmp.replace (SUSPENDED_ROXIEKEY, SRK)

  q_ind = line_tmp.find(SUSPENDED_PACKAGE, 1)
  if (q_ind >= 0):
    line_tmp = line_tmp.replace (SUSPENDED_PACKAGE, SP)

    
  # add ameliorated string to the result list
  new_text.append(line_tmp)

# close input
fin.close ()  


# Format
# First, find out the longest query name  
max_len = 0
long_query = ""
for line in new_text:
  q_i = line.find(' ', 1)
  if (q_i > max_len):
    max_len = q_i
    long_query = line[0:q_i]

    
# now format:
spaces = "                                        "
format_text = []
for line in new_text:
  formatted_line = line
  q_i = line.find(' ', 1)
  if ((q_i < max_len) and (q_i > 0)):
    formatted_line = line[0:q_i] + spaces[0:max_len-q_i] + line[q_i:]

  format_text.append (formatted_line)

    
# Finally, create an output file (overwrite, if exists)
fout = open ("_dev.res", 'w')

# write legend and helpers
fout.write ("Longest query name: " + str(max_len) + " chars: " + long_query)
fout.write ("\n\nLegend:")
fout.write ("\n\t" + SI  + " == " + SUSPENDED_LAYOUT)
fout.write ("\n\t" + SSK + " == " + SUSPENDED_SUPERKEY)
fout.write ("\n\t" + SRK + " == " + SUSPENDED_ROXIEKEY)
fout.write ("\n\t" + SP + " == " + SUSPENDED_PACKAGE)
fout.write ("\n\n")


# write output line by line
for line in format_text:
  fout.write (line)
fout.write ("\n")
fout.close ()
