def getMainFileName(filename):
    i = 0
    mainname = ""
    while True:
        if filename[i] == '.':
            break
        mainname += filename[i]
        i += 1
    return mainname

def openFile(filename):
    objfilename = getMainFileName(filename)
    objfilename = objfilename + ".obj"
    objfile = open(objfilename, "w")
    return objfile

def writeHeader(file, name, starting, proglen):
    header = "H" + programname(name)
    header += hexstrToWord(hex(starting))
    header += hexstrToWord(hex(proglen))
    header += "\n"
    file.write(header)
    
def programname(name):
    n = 6 - len(name)
    for i in range(0, n):
        name = name + ' '
    return name

def writeText(file, starting, tline):
    textrecord = "T" + hexstrToWord(hex(starting))
    l = hex(int(len(tline)/2))
    l = l[2:]
    
    n = 2 - len(l)
    for i in range(0, n):
        l = '0' + l
    
    l = l.upper()
    textrecord += l
    textrecord += tline
    textrecord += "\n"
    file.write(textrecord)
    
def writeEnd(file, address):
    endrecord = "E" + hexstrToWord(hex(address))
    file.write(endrecord)
    file.close()
    
def hexstrToWord(hexstr):
    hexstr = hexstr.upper() #將全部英文字母變成大寫
    hexstr = hexstr[2:] #將16進位開頭的「0x」字首去掉
    n = 6 - len(hexstr) #最多補六個0
    for i in range(0, n): #補0
        hexstr = '0' + hexstr    
    return hexstr

    
