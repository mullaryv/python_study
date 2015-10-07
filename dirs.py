import os, os.path

cur_dir = os.getcwd()
print ('current dir: ', cur_dir)

target_dir = 'C:\\Mull'

#indent = ''

def dirContent (parent, d, indent) :
    full_name=parent+os.sep+d
    if (os.path.isfile (full_name)):
      print (indent+d)
      return
#    cfile = d+os.sep+el
    print (indent+'[' + full_name +']')
    lyst = os.listdir (full_name)
    for el in lyst: 
      if (el=='repos'):
        print ('...skipped: repos')
      else:
        dirContent (full_name, el, indent+'  ')
"""
if (os.path.isdir(cfile)):
        print (cfile+'[D]')
      else:
        print (el)
"""   
dirContent (target_dir,'arc','')
