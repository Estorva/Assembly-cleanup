'''
    Synopsis: extracts necessary block from raw dump file
    Usage:    python assembly.py <raw assembly> [output file]
              a list of compressed instructions can be found at the end of this file
    Date:     2019.5.9
'''

import os
import sys

def main(output_name):
    r = False               # flag, true when (r)eading lines in main block
    v = False               # flag, true when reading local (v)ariables
    psd = []                # Processed section
    fs = []                 # future section
    js = []                 # jump section
    h = []                  # history
    cp = ""                 # current position, assigned as first addr of the section
    a = 0                   # Make v false after two blank lines after ".rodata"

    with open(sys.argv[1], 'r') as f:
        ss = f.readlines()
        # (s)entence(s) = (f)ile.readlines()

        js.append((0, 'main'))

        while True:
            fs = js[:]
            fs.sort(key=lambda x: x[0])
            js.clear()

            for s in ss:
                # for (s)entence in ss
                if s[0] == '#':
                    continue
                    # skip comment lines

                if s == '\t...\n':
                    continue

                if s == '\n':
                    # empty line
                    if r:
                        r = False
                        fs.sort(key=lambda x: x[0]) # sort to be processed blocks
                                                    # by their first address

                        print(fs)
                    continue

                ws = s.strip('\n').split()
                # (w)ord(s) = s.split()

                if len(ws) > 1 and len(fs) > 0 and ws[1] == "<" + fs[0][1] + ">:":
                    r = True
                    psd.append("<" + fs[0][1] + ">:\n")
                    h.append(fs.pop(0)[1])
                    print("Recording block " + h[-1])
                    cp = int(ws[0], 16)
                    continue

                if r:
                    # read lines in main block
                    # parse four kinds of instruction:
                    # 1. addi sp,sp,-32
                    # 2. sw   s0,28(sp)
                    # 3. li   a5,1
                    # 3. jalr ra
                    # 4. ret
                    print("Recording " + s.strip('\n'))
                    psd.append(s)

                    if len(ws) > 3 and ws[-1][-1] == '>' and ws[-3] != '#' and '+' not in ws[-1]:
                            name = ws[-1].lstrip('<').strip('>')
                            addr = int(ws[-2].split(',')[-1], 16)
                            if name not in h:
                                if addr < cp:
                                    js.append((addr, name))
                                else:
                                    fs.append((addr, name))


            if len(js) == 0:
                break
        # while true

        for s in ss:
            if s == '\n':
                # empty line
                if v:
                    a += 1
                if a == 2:
                    v = False
                continue

            if len(s.split()) > 1 and s.split()[-1] == ".rodata:":
                # local variables
                v = True
                psd.append("Data memory:\n")
                continue

            if v:
                # Lines in this block look like this:
                # 6c782:	0000                	unimp
                # The instruction is meaningless
                if s[-3:] == ">:\n": continue
                if s == '\t...\n': continue
                print("Recording " + s.strip('\n'))
                psd.append(s)

        # for s in ss

        o = open(output_name, 'w+')
        for p in psd:
            o.write(p)


if __name__ == '__main__':
    assert len(sys.argv) == 2 or len(sys.argv) == 3, "Usage: assembly.py <raw assembly> [output]"
    if len(sys.argv) == 3:
        output_name = sys.argv[2]
    else:
        output_name = "assembly_raw.txt"

    main(output_name)
