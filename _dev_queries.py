# formats deployment log into some of a nice view

# define text to replace with acronyms
SI = "~SI"
SSK = "~SK"
SRK = "~SR"
SP = "~SP"

# dictionary: defines text replacements
replacements = {
  SI :"is being loaded in suspended state because In index",
  SSK:"is being loaded in suspended state because SuperKey",
  SRK:"is being loaded in suspended state because Roxie server key file",
  SP :"is being loaded in suspended state because PACKAGE_ERROR: Compulsory SuperFile"
}

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

  # replace all known long description with abbreviations;
  # only one will be there, but there's no need to optimize it
  line_tmp = line_tmp.replace (replacements[SI], SI)
  line_tmp = line_tmp.replace (replacements[SSK], SSK)
  line_tmp = line_tmp.replace (replacements[SRK], SRK)
  line_tmp = line_tmp.replace (replacements[SP], SP)
    
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
# TODO: most likely there'sa better way, but so far it suffices
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
fout.write ("\n\t" + SI  + " == " + replacements[SI])
fout.write ("\n\t" + SSK + " == " + replacements[SSK])
fout.write ("\n\t" + SRK + " == " + replacements[SRK])
fout.write ("\n\t" + SP + " == " + replacements[SP])
fout.write ("\n\n")


# write output line by line
for line in format_text:
  fout.write (line)
fout.write ("\n")
fout.close ()
