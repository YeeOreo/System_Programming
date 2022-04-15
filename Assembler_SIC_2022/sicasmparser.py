import sic

def readfile(srcfile):
    try:
        with open(srcfile, "r") as fp:
            return fp.readlines()
    except:
            return None
"""
處理讀取檔案的每一行字元
1.先檢查有沒有註解符號或換行符號，有就忽略，沒有代表為指令(類型待確認)
2.確認指令合不合法
3.回傳合法的回傳指令格式
合法的指令格式有：
(1) label + opcode + operand
(2) label + opcode
(3) opcode + operand
(4) opcode(Directive instruction)
"""
def decompositLine(line):

    if len(line) > 0:
        if line[0] == '.':      # 以「.」作為註解符號
            return (None, None, None)
        if line[0] == '\n':
            return (None, None, None)
    # python的split函數可以用「空格」將string分割
    tokens = line.split()
    if len(tokens) == 1: # 檢查是否為(4)指令格式
        if isOpcodeOrDirective(tokens[0]) == False:
            print("Your assembly code has problem.")
            return (None, None, None)
        return (None, tokens[0], None) # 只有opcode的指令 e.g. RSUB
    elif len(tokens) == 2: # 檢查是否為(2)、(3)指令格式
        if isOpcodeOrDirective(tokens[0]) == True: # (3)opcode + operand
            return (None, tokens[0], tokens[1])
        elif isOpcodeOrDirective(tokens[1]) == True: # (2)label + opcode
            return (tokens[0], tokens[1], None)
        else:
            print("Your assembly code has problem.")
            return (None, None, None)
    elif len(tokens) == 3:
        if isOpcodeOrDirective(tokens[1]) == True:
            return (tokens[0], tokens[1], tokens[2]) # (1)label + opcode + operand
        else:
            print("Your assembly code has problem.")
            return (None, None, None)
    return (None, None, None)
    
def isOpcodeOrDirective(token):
    if sic.isInstruction(token) == True:
        return True
    if sic.isDirective(token) == True:
        return True
    return False