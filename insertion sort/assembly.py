'''
    Synopsis: cleans up the assembly code
    Usage:    python assembly.py <raw assembly> [block]
              specify block to extract a certain block, default: main
              a list of compressed instructions can be found at the end of this file
    Date:     2019.5.9
'''

import os
import sys

def translate_hex(args):
    # Replace words starting w/ "0x" to their decimal form
    # Address after some commands must also be translated
    for i in range(len(args)):
        if args[i][0:2] == "0x":
            args[i] = str(int(args[i], 16))
    return args

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
        elif args[i][0:2] == '0x':
            pass
        else:
            try:
                int(args[i][1])
            except ValueError:
                # string cannot convert into int
                raise NotImplementedError("Unknown register name: " + args[i]) from None
            except IndexError:
                pass # dirty trick to get the program to work
    return args

def expand(il):
    '''
        Given a list of tuples (a string and a dict), on encountering a tuple
        whose 'nm' calls for expansion, modify this instruction, and insert
        necessary instructions after this one.
        Returns a new list of tuples.
        li rd imm -> (lui...) ori...

    '''
    ls = []                             # (l)ist of (s)ubinstructions

    for _, i in il:
        nm = i['nm']
        args = i['args']

        # = creates a reference, not a copy, BAD PYTHON
        new1 = i.copy()
        new2 = i.copy()

        if nm == "li":
            # load upper 20 bits of imm w/ lui and lower 12 bits w/ ori
            imm = int(args[1])
            u = imm >> 12
            l = imm & 0xFFF
            if (u != 0):
                new1['nm'] = 'lui'
                new1['args'] = [args[0], str(u)]
                new1['hex'] = '########'
                new2['nm'] = 'ori'
                new2['args'] = [args[0], args[0], str(l)]
                new2['hex'] = '########'
                ls.append((_, new1))
                ls.append(("", new2))
            else:
                new1['nm'] = 'addi'
                new1['args'] = [args[0], '0', str(u)]
                ls.append((_, new1))

        elif nm == "ret":
            if len(i['hex']) == 4:
                # compressed
                new1['nm'] = 'c.jr'
                new1['args'] = ['1']
            else:
                new1['nm'] = 'jalr'
                new1['args'] = ['0', '1', '0']
            ls.append((_, new1))

        elif nm == "mv":
            new1['nm'] = 'addi'
            new1['args'] = [args[0], args[1], '0']
            ls.append((_, new1))

        elif nm == "j":
            new1['nm'] = 'jal'
            new1['args'] = ['0', args[0]]
            ls.append((_, new1))

        elif nm == "jalr" and len(args) == 2:
            new1['nm'] = 'jalr'
            new1['args'] = ['1', args[0], '0']
            ls.append((_, new1))

        elif nm == "nop":
            new1['nm'] = 'addi'
            new1['args'] = ['0', '0', '0']
            ls.append((_, new1))

        elif nm == "main.ret":
            # new1: nop = addi 0 0 0
            # new2: j -4 = jal 0 -4
            new1['nm'] = 'addi'
            new1['args'] = ['0', '0', '0']
            new1['hex'] = '########'
            new2['nm'] = 'jal'
            new2['args'] = ['0', '-4']
            new2['hex'] = '########'
            ls.append((_, new1))
            ls.append(("", new2))

        else:
            # Nothing to expand: copy args to ls
            ls.append((_, i))

    return ls



def main():
    il = []                 # (i)nstruction (l)ist
    bnl = []                # (b)lock (n)ame (l)ist
    block_name = "main"     # wont parse until <main>, assuming all subprocesses
                            # comes after <main>
    data = []
    read_data = False

    # Run thru the file, record the blocks and their first instruction address
    # Record the offsets of jump instructions
    # Change the address of all instructions according to their instruction length

    with open(sys.argv[1], 'r') as f:
        ss = f.readlines()
        # (s)entence(s) = (f)ile.readlines()

        # build our database
        for s in ss:
            # for (s)entence in ss

            if s[-3:] == ">:\n":
                # new block
                name = s.lstrip('<').strip('>:\n')
                bnl.append((name, []))

        bd = dict(bnl) # dictionary
        pc = 0xa00

        for s in ss:
            if s[0] == '#':
                continue
                # skip comment lines

            if s == "Data memory:\n":
                read_data = True
                continue

            if s[0] == '<':
                block_name = s.lstrip('<').strip('>:\n')
            elif not read_data:
                # instruction
                ws = s.strip('\n').split() # (w)ord(s)

                if len(ws) == 5:
                    # a jump instruction (j-, b-)
                    jdb = ws[4].lstrip('<').split('+')[0].strip('>') # (j)ump (d)estination (b)lock
                    if '+' in ws[4]:
                        offset = ws[4].strip('>').split('+')[-1] # a hex
                    else:
                        offset = "0x0"
                else:
                    jdb = ""
                    offset = "0x0"

                # determine args
                if len(ws) > 3:
                    args = ws[3].split(',')
                else:
                    args = []

                # specially handle ret of main
                # the end of a main must be a loop of nop
                if block_name == 'main' and ws[2] == 'ret':
                    ws[2] = 'main.ret'

                i = {
                    'ad':   ws[0].strip(':'),
                    'hex':  ws[1],
                    'nm':   ws[2],
                    'args': args,
                    'jdb':  jdb,
                    'jdi':  "",
                    'os':   int(offset, 16)
                }
                bd[block_name].append((ws[0].strip(':'), i))
                # In bd, a key is mapped to a dict, which in turn
                # maps an address to an instruction (instr are identified
                # by their raw address)
            else:
                # print data memory entries
                ws = s.strip('\n').split()
                data.append(hex(pc) + ' ' + ws[1] + '\n')
                pc += len(ws[1]) // 2

        pc = 0

        # replace destinations of jump instructions and
        for _, il in bd.items():
            for _, i in il:
                if i['jdb'] != "":
                    # This instruction has a jump destination,
                    # replace the destination w/
                    # the raw address of the destination instruction
                    # jd: destination block -> raw address of dest. instr.
                    start = int(bd[i['jdb']][0][0], 16)
                    offset = i['os']
                    i['jdi'] = hex(start + offset)

        # normalize expression of offsets
        for _, il in bd.items():
            for _, i in il:
                if i['args'] != [] and i['args'][-1][-1] == ')':
                    args_ = i['args'].pop(-1)    # pop() returns the removed entry
                    args_ = args_.split('(')
                    args_[1] = args_[1].strip(')')
                    i['args'].append(args_[1])
                    i['args'].append(args_[0])

        # expand register name
        for _, il in bd.items():
            for _, i in il:
                i['args'] = link_register(i['args'])

        # expand pseudo instructions
        for _, il in bd.items():
            bd[_] = expand(il)

        # rearrange address and add .c prefix
        for _, il in bd.items():
            for _, i in il:
                i['ad'] = hex(pc)
                pc += len(i['hex']) // 2
                # 32bit instruction makes pc + 4, 16bit + 2

                if len(i['hex']) == 4 and i['nm'][0:2] != "c.":
                    i['nm'] = "c." + i['nm']

        # resolute jump destination
        for _, il in bd.items():
            for _, i in il:
                if i['jdb'] != "":
                    for addr, instrdict in bd[i['jdb']]:
                        if addr == i['jdi'][2:]:
                            # absolute:
                            # i['args'][-1] = instrdict['ad']
                            # relative:
                            i['args'][-1] = hex(int(instrdict['ad'], 16) - int(i['ad'], 16))
                            i['hex'] = '#'*len(i['hex']) # invalidate this hex


        o = open(sys.argv[2], 'w+')             # (o)utput
        o.write('// Instructions:\n')
        for _, il in bd.items():
            for _, i in il:
                o.write(i['ad'].ljust(5) + ' ' + i['hex'].ljust(9) + ' ' + i['nm'] + ' ' + ' '.join(i['args']) + '\n')
        o.write('// Data:\n')
        for d in data:
            o.write(d)

        o.close()


if __name__ == '__main__':
    assert len(sys.argv) == 3, "Usage: assembly.py <raw assembly> <output>"

    main()
