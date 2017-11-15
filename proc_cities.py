# creates a table of country objects (I'm interested monstly in cities)
# http://download.geonames.org/export/dump/

'''
geonameid         : integer id of record in geonames database
name              : name of geographical point (utf8) varchar(200)
asciiname         : name of geographical point in plain ascii characters, varchar(200)
alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
latitude          : latitude in decimal degrees (wgs84)
longitude         : longitude in decimal degrees (wgs84)
feature class     : see http://www.geonames.org/export/codes.html, char(1)
feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
country code      : ISO-3166 2-letter country code, 2 characters
cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
admin3 code       : code for third level administrative division, varchar(20)
admin4 code       : code for fourth level administrative division, varchar(20)
population        : bigint (8 byte int) 
elevation         : in meters, integer
dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
modification date : date of last modification in yyyy-MM-dd format
'''

import sys, codecs


ALT_NAMES_MAX = 3               #the number of alternative names to keep
MIN_CITY_POPULATION = 20000     #cities with less than that pop. will be dropped off


# create an ECL-safe string
def clean_word (line):
  return line.replace('\'', '\\\'')
  

#process each line one by one  
def process_object (lines):
  for line in lines:

    k = line.find ('\n')
    if k>0:
      line = line[0:k]
  
    words = line.split('\t')
    num_words = len (words) 

    # take only cities
    if (num_words < 6 or words[6] != 'P'): continue
    # take only nig enough cities
    if (num_words < 14 or int (words[14]) < MIN_CITY_POPULATION) : continue

    #create a string which will represent a raw in inline DATASET
    s = ''

    for i in range (num_words):
      if (i in [4,5,6,7,9,10,11,12,13,15,16,17,18]) : continue 

      if s != '': s += ', '

      word = words[i]
      #take only ~~some~~ of the alternative names (third word):
      if i==3:
        #alt_str_len = len (words[i])
        commas = 0
        ind = 0  
        for k in words[3]:
          if k == ',': commas += 1
          if commas == ALT_NAMES_MAX:
            word = words[3][0:ind]
            break
          ind += 1 

      word = clean_word(word)

      s += '\'' + word + '\''


    yield '  {' + s + '},\n'



#read file name, open file for reading 
if len(sys.argv) < 2:
  print ('  !Provide a file name containing geo-objects.')
  exit(-1) 

fname = sys.argv[1]

#input file
fin = open (fname + '.txt', 'r', encoding='utf-8')

#output file
fout = open (fname + '.res', 'w', encoding='utf-8')
for line in process_object(fin):
  fout.write(line)

fin.close()
fout.close()
  