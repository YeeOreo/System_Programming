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
    objfile = open(objfilename, "w" , newline='\n')
    # Windows 換行字元：\r\n
    return objfile

def writeHeader(file, name, starting, proglen):
    header = "H" + programname(name)
    header += hexstrToWord(hex(starting))
    header += hexstrToWord(hex(proglen))
    header += "\n"
    file.write(header)
    
def programname(name):
    n = 6 - len(name)      #Head Record最多只有7 bits
    for i in range(0, n):  #空白的一律在後面補空白
        name = name + ' '
    return name
"""撰寫Text Record"""
def writeText(file, starting, tline):
    #---column 1(T) + column 2~7---(整段Text Record的starting address)
    textrecord = "T" + hexstrToWord(hex(starting)) #Ｔ接上整段Text Record的Starting Address
    l = hex(int(len(tline)/2))  #1個指令以機器碼表示有3 Bytes, 而在obj file裡以16進位字元表示-
    #1個指令在obj file長度為6個16進位字元，(1個16進位字元為0.5 byte，2個16進位字元為1 byte)
    #因此6個16進位字元「除2」 = 3 bytes
    l = l[2:] #去掉16進位制「0x」字首
    #---column 8~9---object code的length
    """補0"""
    n = 2 - len(l) 
    for i in range(0, n):
        l = '0' + l  # 如果length只有各位數，前面補「0」
    
    l = l.upper() # 16進位制的A~F轉成uppercase
    textrecord += l
    textrecord += tline
    textrecord += "\n"
    file.write(textrecord)
"""撰寫End Record"""    
def writeEnd(file, address):
    endrecord = "E" + hexstrToWord(hex(address))
    file.write(endrecord)
    file.close()
    # 將16進位的字串傳進來
def hexstrToWord(hexstr):
    hexstr = hexstr.upper() #將全部英文字母變成大寫
    hexstr = hexstr[2:] #將16進位字串開頭的「0x」字首去掉
    n = 6 - len(hexstr) #最多補六個0(從opcode的部分開始補，完全沒opcode就補六個0)
    for i in range(0, n): #補0
        hexstr = '0' + hexstr    
    return hexstr

    
