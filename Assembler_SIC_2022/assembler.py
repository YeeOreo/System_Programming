import sys

import sic
import sicasmparser

import objfile
# BYTE指令專用，處理BYTE C'ASCII字元'指令
# 去除「C」、「'」轉換為16進位字元後視情況補0
def processBYTEC(operand):
    constant = ""
    for i in range(2, len(operand)-1): # loop的範圍：去除「C」、前後2個「'」
        tmp = hex(ord(operand[i])) # ord函數會回傳ASCII(10進位)的字元
        tmp = tmp[2:] # 去除16進位「0x」字首
        if len(tmp) == 1: # 一個16進位字元有2 bit，如果只有1 bit，前面補「0」
            tmp = "0" + tmp
        tmp = tmp.upper() # Object File的16進位字元皆為大寫
        constant += tmp
    return constant # 回傳名為constant的16進位字串

# PASS2 使用：將整行的組合語言(一般指令，不為假指令(Directive Instruction)轉換為機器碼
# 但在下方實作時用Integer(變數為instruction)來存放機器碼
# (因此會需要移位或set bit(使特定位元為1) ) 補充：相反的，clear bit為使特定位元為0
def generateInstruction(opcode, operand, SYMTAB): #一個指令有3 bytes
    instruction = int(sic.OPTAB[opcode] * 65536) # opcode 需往左邊移動16格(2^16 = 65536)
    if operand != None: # 如果有operand
        if operand[len(operand)-2:] == ',X': # 如果operand(string型態)最後2格是「,X」
            instruction += 32768 # 在instruction第15個bit set 1(2^15 = 32768)
            operand = operand[:len(operand)-2] # 將「,X」去掉，存入operand
        if operand in SYMTAB: # 如果operand是constant則查表
            instruction += int(SYMTAB[operand])
        else:
            return ""
    return objfile.hexstrToWord(hex(instruction))


if len(sys.argv) != 2: # 在Terimal 傳入的參數不等於 2(argv為在傳入本python檔案的參數之list，第1個是本程式名稱，第2個是在Terimal輸入的參數)
    # len(sys.argv)即傳回argv的list參數個數，等同C、C++、Java的int argc
    print("Usage: python3 assembler.py <source file>")
    sys.exit()
    
lines = sicasmparser.readfile(sys.argv[1])
# argv[0]為執行程式(本程式)名稱，argv[1] 為在Terimal輸入的檔案參數
# readfile會回傳所有的line(列表list)給lines變數(以換行字元作切割)
# e.g. lines[0] 為第一行；line[1] 為第二行 e.t.c
SYMTAB = {}

# PASS 1 
"""
製造SYMTAB(Symbol Table)、紀錄整份程式檔案(由LOCCTR(Location Counter)計算)之長度(bytes)
"""
for line in lines: 
    t = sicasmparser.decompositLine(line)
# 將lines切成一行一行的line(4種合法的指令格式，細節在「sicasmparser.py」及下方有寫)
    if t == (None, None, None):
        continue
    
    if t[1] == "START": # Directive Instruction "START"
        STARTING = int(t[2], 16) # 將starting address由16進位轉成10進位紀錄在STARTING變數中
        LOCCTR = int(STARTING)
    
    if t[1] == "END": # Directive Instruction "END"
        proglen = int(LOCCTR - STARTING) #計算program length
        break
    # 建立Symbol Table
    if t[0] != None:
        if t[0] in SYMTAB:  # 重複的labels
            print("Your assembly code has problem.")
            continue
        SYMTAB[t[0]] = LOCCTR  # 將未重複的label紀錄到Symbol Table 
        # Symbol Table本身為Dictionary的資料結構，key為t[0](指令格式的label)-
        # value為Location Counter
    """
    指令格式有：
    (1) label + opcode + operand
    (2) label + opcode
    (3) opcode + operand
    (4) opcode(Directive instruction)
    以下以：
    t[0] = label
    t[1] = opcode
    t[2] = operand 表示
    """
    #處理Location Counter
    if sic.isInstruction(t[1]) == True: # 如果是SIC的instruction
        LOCCTR = LOCCTR + 3                 # SIC的每一個指令長3 bytes
    elif t[1] == "WORD":    # 1 word = 3 bytes
        LOCCTR = LOCCTR + 3
    elif t[1] == "RESW":    # 以word(1 word = 3 bytes)為單位保留記憶體空間
        LOCCTR = LOCCTR + (int(t[2])*3) #保留 3 * operand(人指定的Word個數) bytes空間
    elif t[1] == "RESB":    # 以byte為單位保留記憶體空間
        LOCCTR = LOCCTR + int(t[2]) # 保留1 byte的記憶體空間
    elif t[1] == "BYTE": # e.g. BYTE C'EOF' e.g.2. BYTE X'454647'
        if t[2][0] == 'C': # 以ASCII code字元表示指定Assembler要保留的記憶體空間
        # ，LOCCTR一律以bytes作計算，1個ASCII code字元為1 byte
            LOCCTR = LOCCTR + (len(t[2]) - 3) # operand去掉「C」、「'」*2個後剩下的ASCII code字元數(bytes)
        if t[2][0] == 'X': # 以16進位字元表示指定Assembler要保留的記憶體空間
            LOCCTR = LOCCTR + ((len(t[2]) - 3)/2) # LOCCTR一律以bytes作計算
        # -3為去掉「X」、「'」*2個後剩下的16進位字元，而16進位字元要轉換為byte，每2個16進位字元為1 bytes。
        # 故16進位字元 / 2 = 剩下的bytes數

print(SYMTAB) 

# PASS 2
"""
依照SYMTAB建造Object File
"""
reserveflag = False # 執行Reserve 記憶體空間的指令時，flag 設為 True

t = sicasmparser.decompositLine(lines[0]) # 讀取第一行並拆成(label,opcode,operand)的格式

file = objfile.openFile(sys.argv[1]) #argv list的第2個參數即為在Terimal輸入的asm檔案
# 「file」變數即為要寫入的Objrct File
LOCCTR = 0 #LOCCTR為Location Counter，像Program Counter一樣，會記錄當前執行的指令
if t[1] == "START":
    LOCCTR = int(t[2], 16)  # 將t[2]的內容(數字)以16進位的基底轉成10進位的integer
    progname = t[0]
STARTING = LOCCTR

objfile.writeHeader(file, progname, STARTING, proglen)  # 寫入Object File的Head Record
""""存放Text Record之變數"""
tline = "" # Text Record有可能不只一行,這個變數紀錄每一行指令(非Directive Instruction)的機器碼
tstart = LOCCTR # 用來存放每一行Text Record的Start Address
# Text Record格式為column 2 ~ 7 為該行Text Record的Starting Address

for line in lines:
    t = sicasmparser.decompositLine(line)

    if t == (None, None, None):
        continue

    if t[1] == "START": # 上面Head Record已寫入Object File中了
        continue

    if t[1] == "END": # 寫入End Record

        if len(tline) > 0:
            objfile.writeText(file, tstart, tline)  # 將Text Record寫入Object File
            
        PROGLEN = LOCCTR - STARTING # 計算整個Object File的length

        address = STARTING
        if t[2] != None:
            address = SYMTAB[t[2]]
            
        objfile.writeEnd(file, address) # 將End Record寫入Object File
        break

    # 一般指令                
    if t[1] in sic.OPTAB:

        instruction = generateInstruction(t[1], t[2], SYMTAB) # 將整行組合語言轉換為機器碼
        
        if len(instruction) == 0: # 指令錯誤時，函式傳回空值
            print("Undefined Symbols: %s" % t[2]) # 提醒人組合語言指令撰寫錯誤
            break
        # LOCCTR此時指向前一個指令，而在SIC中，一個指令長度一律為3 bytes，因此LOCCTR + 3
        # 在Text Record中，column 10 ~ 69為Object Code存放的位置
        # 而Object Code總共可以存放69 - 10 + 1 = 60個16進位字元，而每6個16進位字元為1個指令
        # 在LOCCTR計算的時候，一律以「byte」為單位(1指令為3 bytes，2個16進位字元為1 bytes)
        # 因此60個16進位字元可以存放 60 / 6 = 10個指令
        # 每個指令3 bytes，3 * 10個指令 = 30 bytes
        # 因此(LOCCTR + 3 - tstart > 30)為檢視有沒有超過當前整個Text Record中Object Code部分-
        # (column 10 ~ 69)的長度(以byte為單位)
        # 如果有，就呼叫writeText函式再寫新的一行Text Record
        # 而如果是reserve word或reserve bytes的指令(而此時reserveflag == True)
        # 一律呼叫writeText函式再寫新的一行Text Record(不換行保留空間將沒有意義)
        # 如果沒有，直接寫進去當前的Text Record
        if (LOCCTR + 3 - tstart > 30) or (reserveflag == True): 
            objfile.writeText(file, tstart, tline) # 將前一行的Text Record寫入Object File
            """下面兩行為換新的一行處理的動作"""
            tstart = LOCCTR # 新一行Text Record機器碼的Starting Address
            tline = instruction # 新一行Text Record的指令機器碼
        else: # 前一行還有空間 or 沒有超過當前Text Record中Object Code部分的長度，直接寫入當前的Text Record
            tline += instruction

        reserveflag = False

        LOCCTR += 3 # 1個WORD也是3個bytes
    # 假指令directive instruction:WORD         
    elif t[1] == "WORD": # 以下的任務為將constant寫入Object File
        # 因為SIC的Object File中是由16進位字元組成的，因此要使用hex函數
        # hex函數會將參數轉為16進位的字串(開頭有「0x」字首)
        # 將16進位字串傳入，會將字首去除和補0傳回                                               
        constant = objfile.hexstrToWord(hex(int(t[2]))) 
        """處理流程與上方的一般指令相同"""
        if (LOCCTR + 3 - tstart > 30) or (reserveflag == True):
            objfile.writeText(file, tstart, tline)
            """下面兩行為換新的一行處理的動作"""
            tstart = LOCCTR # 新一行Text Record機器碼的Starting Address
            tline = constant # 新一行Text Record的指令機器碼
        else:
            tline += constant
        
        reserveflag = False

        LOCCTR += 3
    # 假指令directive instruction：BYTE         
    elif t[1] == "BYTE": # 以下的任務為將constant寫入Object File

        if t[2][0] == 'X': # 以16進位字元表示，保留X'0x數字'/2(bytes)的記憶體空間
            operandlen = int((len(t[2]) - 3)/2) # -3為去掉「C」、「'」*2個，除2為16進位字元轉換為bytes長度
            # 補充說明：operand以機器碼表示有1 Bytes, 而在obj file裡以16進位字元表示-
            # 1個operand在obj file長度為2個16進位字元，(1個16進位字元為0.5 byte，2個16進位字元為1 byte)
            # 因此2個16進位字元「除2」 = 1 bytes
            constant = t[2][2:len(t[2])-1] # 去除「X」前面的「'」、最後的「'」
        elif t[2][0] == 'C': # 以ASCII code表示的字元，1個ASCII code字元為1 byte
            operandlen = int(len(t[2]) - 3) #operand去掉「C」、「'」*2個剩下的bytes數   
            constant = processBYTEC(t[2]) # processBYTEC函數會去除「C」、「'」轉換為16進位字元後視情況補0
        """處理流程與上方的一般指令相同"""    
        if (LOCCTR + 3 - tstart > 30) or (reserveflag == True):    
            objfile.writeText(file, tstart, tline)
            """下面兩行為換新的一行處理的動作"""
            tstart = LOCCTR # 新一行Text Record機器碼的Starting Address
            tline = constant # 新一行Text Record的指令機器碼
        else:
            tline += constant

        reserveflag = False

        LOCCTR += operandlen
    # 假指令directive instruction：RESB、RESW不用產生Object Code，但LOCCTR還是需要計算
    # 這兩個指令是告訴Assembler保留記憶體，並讓下個指令寫進Object Code時強制換行
    # 注意：上方的BYTE、WORD指令會產生Object Code，但下個指令不用強制換行！
    elif t[1] == "RESB":
        LOCCTR += int(t[2]) # 保留operand數量的Bytes
        reserveflag = True # 強制換行
    elif t[1] == "RESW":
        LOCCTR += (int(t[2]) * 3) #保留operand數量的Words
        reserveflag = True # 強制換行
    else:
        print("Invalid Instruction / Invalid Directive")
        