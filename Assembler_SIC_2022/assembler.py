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
    instruction = int(sic.OPTAB[opcode] * 65536)
    if operand != None:
        if operand[len(operand)-2:] == ',X':
            instruction += 32768
            operand = operand[:len(operand)-2]
        if operand in SYMTAB:
            instruction += int(SYMTAB[operand])
        else:
            return ""
    return objfile.hexstrToWord(hex(instruction))


if len(sys.argv) != 2:
    print("Usage: python3 assembler.py <source file>")
    sys.exit()
    
lines = sicasmparser.readfile(sys.argv[1])

SYMTAB = {}

# PASS 1
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
        if t[0] in SYMTAB:
            print("Your assembly code has problem.")
            continue
        SYMTAB[t[0]] = LOCCTR
    
    if sic.isInstruction(t[1]) == True:
        LOCCTR = LOCCTR + 3
    elif t[1] == "WORD":
        LOCCTR = LOCCTR + 3
    elif t[1] == "RESW":
        LOCCTR = LOCCTR + (int(t[2])*3)
    elif t[1] == "RESB":
        LOCCTR = LOCCTR + int(t[2])
    elif t[1] == "BYTE":
        if t[2][0] == 'C':
            LOCCTR = LOCCTR + (len(t[2]) - 3)
        if t[2][0] == 'X':
            LOCCTR = LOCCTR + ((len(t[2]) - 3)/2)
        

print(SYMTAB)

# PASS 2

reserveflag = False

t = sicasmparser.decompositLine(lines[0])
    
file = objfile.openFile(sys.argv[1])

LOCCTR = 0
if t[1] == "START":
    LOCCTR = int(t[2], 16)
    progname = t[0]
STARTING = LOCCTR

objfile.writeHeader(file, progname, STARTING, proglen)

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
            objfile.writeText(file, tstart, tline)
            
        PROGLEN = LOCCTR - STARTING

        address = STARTING
        if t[2] != None:
            address = SYMTAB[t[2]]
            
        objfile.writeEnd(file, address)
        break

                    
    if t[1] in sic.OPTAB:

        instruction = generateInstruction(t[1], t[2], SYMTAB)
        
        if len(instruction) == 0:
            print("Undefined Symbole: %s" % t[2])
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
        