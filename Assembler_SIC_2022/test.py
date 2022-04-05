def main():
    print(generateInstruction(0x18,)) #ADD	FIVE

def generateInstruction(opcode, operand, SYMTAB):
    instruction = int(sic.OPTAB[opcode] * 65536) # opcode 需往左邊移動15格
    if operand != None:
        if operand[len(operand)-2:] == ',X': # 如果operand最後2格是「,X」
            instruction += 32768 # 在instruction第15個bit set 1
            operand = operand[:len(operand)-2]
        if operand in SYMTAB:
            instruction += int(SYMTAB[operand])
        else:
            return ""
    return objfile.hexstrToWord(hex(instruction))

def hexstrToWord(hexstr):
    hexstr = hexstr.upper() #將全部英文字母變成大寫
    hexstr = hexstr[2:] #將16進位開頭的「0x」字首去掉
    n = 6 - len(hexstr) #最多補六個0
    print(n)
    for i in range(0, n): #補0
        hexstr = '0' + hexstr    
    return hexstr

if __name__ == '__main__':
    main()