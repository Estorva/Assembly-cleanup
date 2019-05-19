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
    block_name = 'main'
    a = 0                   # Make v false after two blank lines after ".rodata"

    with open(sys.argv[1], 'r') as f:
        ss = f.readlines()
        # (s)entence(s) = (f)ile.readlines()
        for s in ss:
            # for (s)entence in ss
            if s[0] == '#':
                continue
                # skip comment lines

            if s == '\n':
                # empty line
                r = False
                if v:
                    a += 1
                if a == 2:
                    v = False
                continue

            if s[-4:-1] == "...":
                # local variable block may end in "..."
                v = False
                continue

            ws = s.strip('\n').split()
            # (w)ord(s) = s.split()
            if len(ws) > 1 and ws[1] == "<" + block_name + ">:":
                r = True
                psd.append("<" + block_name + ">:\n")
                continue

            if len(ws) > 1 and ws[-1] == ".rodata:":
                # local variables
                v = True
                psd.append("Data memory:\n")
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

                if len(ws) > 3 and ws[-1][-1] == '>' and ws[-3] != '#':
                        block_name = ws[-1].lstrip('<').strip('+').strip('>')


            if v:
                # Lines in this block look like this:
                # 6c782:	0000                	unimp
                # The instruction is meaningless
                if s[-3:] == ">:\n": continue
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
