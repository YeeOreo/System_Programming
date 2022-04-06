import sys

import sic
import sicasmparser

import objfile

def processBYTEC(operand):
    constant = ""
    for i in range(2, len(operand)-1):
        tmp = hex(ord(operand[i]))
        tmp = tmp[2:]
        if len(tmp) == 1:
            tmp = "0" + tmp
        tmp = tmp.upper()
        constant += tmp
    return constant

def generateInstruction(opcode, operand, SYMTAB):
    instruction = int(sic.OPTAB[opcode] * 65536) # opcode 需往左邊移動15格
    if operand != None:
        if operand[len(operand)-2:] == ',X': # 如果operand最後2格是「,X」
            instruction += 32768 # 在instruction第15個bit set 1
            operand = operand[:len(operand)-2] # 將「,X」去掉，存入operand
        if operand in SYMTAB:
            instruction += int(SYMTAB[operand])
        else:
            return ""
    return objfile.hexstrToWord(hex(instruction))


if len(sys.argv) != 2: # 在Terimal 傳入的參數不等於 2(argv為在傳入本python檔案的參數之list，第1個是本程式名稱，第2個是在Terimal輸入的參數)
    # len(sys.argv)即傳回argv的list參數個數，等同C、C++、Java的int argc
    print("Usage: python3 assembler.py <source file>")
    sys.exit()
    
lines = sicasmparser.readfile(sys.argv[1])

SYMTAB = {}

# PASS 1
"""
製造SYMTAB(Symbol Table)、紀錄整份程式檔案(由LOCCTR(Location Counter)計算)之長度(bytes)
"""
for line in lines:
    t = sicasmparser.decompositLine(line)

    if t == (None, None, None):
        continue
    
    if t[1] == "START":
        STARTING = int(t[2], 16)
        LOCCTR = int(STARTING)
    
    if t[1] == "END":
        proglen = int(LOCCTR - STARTING)
        break
    
    if t[0] != None:
        if t[0] in SYMTAB:  # 重複的labels
            print("Your assembly code has problem.")
            continue
        SYMTAB[t[0]] = LOCCTR   
    
    if sic.isInstruction(t[1]) == True:
        LOCCTR = LOCCTR + 3                 # 每一個指令長3 bytes
    elif t[1] == "WORD":    # 1 word = 3 bytes
        LOCCTR = LOCCTR + 3
    elif t[1] == "RESW":    # RESERVE the indicated number of words for a data area | 以word(1 word = 3 bytes)為單位保留記憶體空間
        LOCCTR = LOCCTR + (int(t[2])*3)
    elif t[1] == "RESB":    # Reserve the indicated number of bytes for a data area | 以byte為單位保留記憶體空間
        LOCCTR = LOCCTR + int(t[2])
    elif t[1] == "BYTE": 
        if t[2][0] == 'C':
            LOCCTR = LOCCTR + (len(t[2]) - 3) # 「C」 不算
        if t[2][0] == 'X':
            LOCCTR = LOCCTR + ((len(t[2]) - 3)/2) # 
        

print(SYMTAB)

# PASS 2
"""
依照SYMTAB建造Object File
"""
reserveflag = False # 執行Reserve 記憶體空間的指令時，flag 設為 True

t = sicasmparser.decompositLine(lines[0])
    
file = objfile.openFile(sys.argv[1]) #argv list的第2個參數即為檔案

LOCCTR = 0
if t[1] == "START":
    LOCCTR = int(t[2], 16)  # 將t[2]的內容(數字)以16進位的基底轉成10進位的integer
    progname = t[0]
STARTING = LOCCTR

objfile.writeHeader(file, progname, STARTING, proglen)  # 寫入Object File的Head Record

tline = ""
tstart = LOCCTR

for line in lines:
    t = sicasmparser.decompositLine(line)

    if t == (None, None, None):
        continue

    
    if t[1] == "START":
        continue

    if t[1] == "END":

        if len(tline) > 0:
            objfile.writeText(file, tstart, tline)  # 寫入Object File的Text Record
            
        PROGLEN = LOCCTR - STARTING

        address = STARTING
        if t[2] != None:
            address = SYMTAB[t[2]]
            
        objfile.writeEnd(file, address) # 寫入Object File的End Record
        break

                    
    if t[1] in sic.OPTAB:

        instruction = generateInstruction(t[1], t[2], SYMTAB)
        
        if len(instruction) == 0: # 指令錯誤時，函式傳回空值
            print("Undefined Symbols: %s" % t[2]) # 指令錯誤
            break

        if (LOCCTR + 3 - tstart > 30) or (reserveflag == True):
            objfile.writeText(file, tstart, tline)
            tstart = LOCCTR
            tline = instruction
        else:
            tline += instruction

        reserveflag = False

        LOCCTR += 3
            
    elif t[1] == "WORD":

        constant = objfile.hexstrToWord(hex(int(t[2])))

        if (LOCCTR + 3 - tstart > 30) or (reserveflag == True):
            objfile.writeText(file, tstart, tline)
            tstart = LOCCTR
            tline = constant
        else:
            tline += constant
        
        reserveflag = False

        LOCCTR += 3
            
    elif t[1] == "BYTE":

        if t[2][0] == 'X':
            operandlen = int((len(t[2]) - 3)/2)
            constant = t[2][2:len(t[2])-1]
        elif t[2][0] == 'C':
            operandlen = int(len(t[2]) - 3)
            constant = processBYTEC(t[2])
            
        if (LOCCTR + 3 - tstart > 30) or (reserveflag == True):
            objfile.writeText(file, tstart, tline)
            tstart = LOCCTR
            tline = constant
        else:
            tline += constant

        reserveflag = False

        LOCCTR += operandlen
            
    elif t[1] == "RESB":
        LOCCTR += int(t[2])
        reserveflag = True
    elif t[1] == "RESW":
        LOCCTR += (int(t[2]) * 3)
        reserveflag = True
    else:
        print("Invalid Instruction / Invalid Directive")
        