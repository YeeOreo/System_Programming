OPTAB = {

    # SIC Instruction Set
    
    "ADD":  0x18,
    "AND":  0x40,
    "COMP": 0x28,
    "DIV":  0x24,
    "J":    0x3C,
    "JEQ":  0x30,
    "JGT":  0x34,
    "JLT":  0x38,
    "JSUB": 0x48,
    "LDA":  0x00,
    "LDCH": 0x50,
    "LDL":  0x08,
    "LDX":  0x04,
    "MUL":  0x20,
    "OR":   0x44,
    "RD":   0xD8,
    "RSUB": 0x4C,
    "STA":  0x0C,
    "STCH": 0x54,
    "STL":  0x14,
    "STSW": 0xE8,
    "STX":  0x10,
    "SUB":  0x1C,
    "TD":   0xE0,
    "TIX":  0x2C,
    "WD":   0xDC
}
# pseudo instruction 假指令，沒有被CPU真正執行的指令，只是用來告訴Assembler做事的指令
DIRECTIVE = [
    "START",
    "END",
    "WORD",
    "BYTE", 
    "RESW",# Reserve Word：叫Assembler在Ojject file中保留1 word(3 bytes)的空間
    "RESB" # Reserve Byte：叫Assembler在Object file中保留1 byte的空間
]
# 假指令
def isDirective(token):
    if token in DIRECTIVE:
        return True
    else:
        return False
# 指令
def isInstruction(token):
    if token in OPTAB:
        return True
    else:
        return False
