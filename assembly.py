'''
    Synopsis: cleans up the assembly code
    Usage:    python assembly.py <raw assembly>
    Date:     2019.5.9
'''

import os
import sys

def link_register(args):
    '''
        Replace register names in list args w/ integers
        Reg     Number
        ra      1
        sp      2
        gp      3
        tp      4
        t0-2    5-7
        fp      8
        s0      8
        s1      9
        a0-7    10-17
        s2-11   18-27
        t3-6    28-31
    '''

    for i in range(len(args)):
        if args[i] == "ra":
            args[i] = '1'
        elif args[i] == "sp":
            args[i] = '2'
        elif args[i] == "gp":
            args[i] = '3'
        elif args[i] == "tp":
            args[i] = '4'
        elif args[i] == "fp":
            args[i] = '8'

        elif args[i][0] == 't':
            # map temporary registers
            try:
                num = int(args[i][1])
            except ValueError:
                raise NotImplementedError("Unknown register name: " + args[i]) from None
            if num < 3:
                args[i] = str(num + 5)
            else:
                args[i] = str(num + 25)

        elif args[i][0] == 's':
            # map saved registers
            try:
                num = int(args[i][1])
            except ValueError:
                raise NotImplementedError("Unknown register name: " + args[i]) from None
            if num < 2:
                args[i] = str(num + 8)
            else:
                args[i] = str(num + 16)

        elif args[i][0] == 'a':
            # map function arguments
            try:
                num = int(args[i][1])
            except ValueError:
                raise NotImplementedError("Unknown register name: " + args[i]) from None
            args[i] = str(int(args[i][1]) + 10)
        else:
            try:
                int(args[i])
            except ValueError:
                # string cannot convert into int
                raise NotImplementedError("Unknown register name: " + args[i]) from None
    return args

def expand(args):
    # Given args (a list of strings, first of which is instruction name),
    # expand the instruction into corresponding sub-instructions
    # and returns a list of sub-instructions, which are list of strings
    # li rd imm -> (lui...) ori...
    ls = []                             # (l)ist of (s)ubinstructions

    if args[0] == "li":
        # load upper 20 bits of imm w/ lui and lower 12 bits w/ ori
        imm = int(args[2])
        u = imm >> 12
        l = imm & 0xFFF
        if (u != 0):
            ls.append(['lui', args[1], str(u)])
            ls.append(['ori', args[1], args[1], str(l)])
        else:
            ls.append(['addi', args[1], '0', str(l)])
    elif args[0] == "ret":
        ls.append(['jalr', '0', '1', '0'])
    elif args[0] == "mv":
        ls.append(['addi', args[1], args[2], '0'])
    elif args[0] == "j":
        ls.append(['jal', '0', args[1]])
    elif args[0] == "jalr" and len(args) == 2:
        ls.append(['jalr', '1', args[1], '0'])
    elif args[0] == "nop":
        ls.append(['addi', '0', '0', '0'])
    else:
        # Nothing to expand: copy args to ls
        ls.append(args)

    return ls


def main():
    r = False               # flag, true when (r)eading lines in main block
    il = []                 # (i)nstruction (l)ist

    with open(sys.argv[1], 'r') as f:
        ss = f.readlines()
        # (s)entence(s) = (f)ile.readlines()
        for s in ss:
            # for (s)entence in ss
            if s == '\n':
                # empty string
                if r:
                    r = False
                continue

            ws = s.split()
            # (w)ord(s) = s.split()
            if len(ws) > 1 and ws[0] == "00000000" and ws[1] == "<main>:":
                r = True
                continue

            if r:
                # read lines in main block
                # parse four kinds of instruction:
                # 1. addi sp,sp,-32
                # 2. sw   s0,28(sp)
                # 3. li   a5,1
                # 3. jalr ra
                # 4. ret
                print("Parsing " + s.strip('\n'))

                i = [ws[2]]                 # (i)nstruction
                if (len(ws) > 3):
                    # len(ws) = 3 when instr = nop or ret
                    args = ws[3].split(',')     # (arg)ument(s), split at ','
                    if len(args) == 2 and args[-1][-1] == ')':
                        # second case
                        # sw rs2,offsef(rs1) -> sw rs2 rs1 offset
                        args_ = args.pop(-1)    # pop() returns the removed entry
                        args_ = args_.split('(')
                        args_[1] = args_[1].strip(')')
                        args.append(args_[1])
                        args.append(args_[0])

                    # Replace register names of args w/ numbers
                    args = link_register(args)
                else:
                    args = []

                # Expand pseudo instructions, must now instruction name & args
                i = i + args                # join two lists
                i = expand(i)               # i = list of list of strings
                for i_ in i:
                    il.append(' '.join(i_) + '\n') # merge strings into a string
        # for s in ss:

        o = open('assembly.txt', 'w+')     # (o)utput
        for i in il:
            o.write(i)

if __name__ == '__main__':
    assert len(sys.argv) == 2, "Usage: assembly.py <raw assembly>"
    main()
