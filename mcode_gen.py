#instr=raw_input('Enter instr:')
#i=instr.split()
import math
import sys

R_type=['add','sub','sll','slt','sltu','xor','srl','sra','or','and']
R_f7=['0000000','0100000','0000000','0000000','0000000','0000000','0000000','0100000','0000000','0000000']
R_f3=['000','000','001','010','011','100','101','101','110','111']

I_type=['addi','slti','sltiu','xori','ori','andi','slli','srli','sral']
I_f3=['000','010','011','100','110','111','001','101','101']

S_type=['sb','sh','sw']
S_f3=['000','001','010']

L_type=['lb','lh','lw','lbu','lhu']
L_f3=['000','001','010','100','101']

B_type=['beq','bne','blt','bge','bltu','bgeu']
B_f3=['000','001','100','101','110','111']

f=open(sys.argv[1],'r')
fw=open(sys.argv[2],'w')
line=f.readlines()
for instr in line:
    if instr == '// Data:\n': break
    if instr[0:2] == '//': continue
    print instr,
    instr_o=""
    i=instr.split()
    i.pop(0) # remove address
    i.append(i.pop(0)) # put hex to last

#R-type
    for k in range(len(R_type)):
        if R_type[k]==i[0] :
            for l in [1, 2, 3]:
                i[l]=str(bin(int(i[l]))).lstrip('0b').zfill(5)
            opcode='0110011'
            funct7=R_f7[k]
            funct3=R_f3[k]
            rs2=i[3]
            rs1=i[2]
            rd=i[1]
            print funct7+'_'+rs2+'_'+rs1+'_'+funct3+'_'+rd+'_'+opcode
            instr_o=funct7+rs2+rs1+funct3+rd+opcode

#I-type

    for k in range(len(I_type)):
        if I_type[k]==i[0] :
            i[1]=str(bin(int(i[1]))).lstrip('0b').zfill(5)
            i[2]=str(bin(int(i[2]))).lstrip('0b').zfill(5)
            if i[0]!='srai':
                if (i[0]=='srli' or i[0]=='slli') and int(i[3], 0)<0:
                    i[3]=str(int(math.pow(2,5)+int(i[3], 0)))
                elif int(i[3], 0)<0:
                    i[3]=str(int(math.pow(2,12)+int(i[3], 0)))
                i[3]=str(bin(int(i[3], 0))).lstrip('0b').zfill(12)
            else:
                if int(i[3], 0)<0:
                    i[3]=math.pow(2,5)+int(i[3])
                i[3]='0100000'+str(bin(int(i[3]))).lstrip('0b').zfill(5)
            opcode='0010011'
            funct3=I_f3[k]
            imm=i[3]
            rd=i[1]
            rs1=i[2]
            print imm+'_'+rs1+'_'+funct3+'_'+rd+'_'+opcode
            instr_o=imm+rs1+funct3+rd+opcode

#S-type

    for k in range(len(S_type)):
        if S_type[k]==i[0] :
            i[1]=str(bin(int(i[1]))).lstrip('0b').zfill(5)
            i[2]=str(bin(int(i[2]))).lstrip('0b').zfill(5)
            if int(i[3], 0)<0:
                i[3]=math.pow(2,12)+int(i[3])
            i[3]=str(bin(int(i[3]))).lstrip('0b').zfill(12)
            opcode='0100011'
            funct3=S_f3[k]
            imm=i[3]
            print imm[0:7]+'_'+i[1]+'_'+i[2]+'_'+funct3+'_'+imm[7:12]+'_'+opcode
            instr_o=imm[0:7]+i[1]+i[2]+funct3+imm[7:12]+opcode


#L-type

    for k in range(len(L_type)):
        if L_type[k]==i[0] :
            i[1]=str(bin(int(i[1]))).lstrip('0b').zfill(5)
            i[2]=str(bin(int(i[2]))).lstrip('0b').zfill(5)
            if int(i[3], 0)<0:
                i[3]=math.pow(2,12)+int(i[3])
            i[3]=str(bin(int(i[3]))).lstrip('0b').zfill(12)
            opcode='0000011'
            funct3=L_f3[k]
            imm=i[3]
            rd=i[1]
            rs1=i[2]
            print imm+'_'+rs1+'_'+funct3+'_'+rd+'_'+opcode
            instr_o=imm+rs1+funct3+rd+opcode

#B-type

    for k in range(len(B_type)):
        if B_type[k]==i[0] :
            i[1]=str(bin(int(i[1]))).lstrip('0b').zfill(5)
            i[2]=str(bin(int(i[2]))).lstrip('0b').zfill(5)
            if int(i[3], 0)<0 :
                i[3]=str(int(math.pow(2,12)+int(i[3], 0)))
            i[3]=str(bin(int(i[3], 0))).lstrip('0b').zfill(12)
            opcode='1100011'
            funct3=B_f3[k]
            imm=i[3]
            rs2=i[2]
            rs1=i[1]
            print imm[0:1]+'_'+imm[2:8]+'_'+rs2+'_'+rs1+'_'+funct3+'_'+imm[8:12]+'_'+imm[1:2]+'_'+opcode
            instr_o=imm[0:1]+imm[2:8]+rs2+rs1+funct3+imm[8:12]+imm[1:2]+opcode

#jal rd imm
    if i[0]=='jal':
        i[1]=str(bin(int(i[1]))).lstrip('0b').zfill(5)
        if int(i[2], 0)<0:
            i[2]=math.pow(2,20)+int(i[2])
        i[2]=str(bin(int(i[2], 0))).lstrip('0b').zfill(20)
        opcode='1101111'
        rd=i[1]
        imm=i[2]
        print imm[0:1]+'_'+imm[10:20]+'_'+imm[9:10]+'_'+imm[1:9]+'_'+rd+'_'+opcode
        instr_o=imm[0:1]+imm[10:20]+imm[9:10]+imm[1:9]+rd+opcode


#jalr rd rs1 imm
    if i[0]=='jalr':
        i[1]=str(bin(int(i[1]))).lstrip('0b').zfill(5)
        i[2]=str(bin(int(i[2]))).lstrip('0b').zfill(5)
        if int(i[3], 0)<0:
            i[3]=math.pow(2,12)+int(i[3])
        i[3]=str(bin(int(i[3]))).lstrip('0b').zfill(12)
        opcode='1100111'
        rd=i[1]
        rs1=i[2]
        imm=i[3]
        print imm+'_'+rs1+'_'+'000'+'_'+rd+'_'+opcode
        instr_o=imm+rs1+'000'+rd+opcode

    if i[0]=='lui':
        rd=str(bin(int(i[1]))).lstrip('0b').zfill(5)
        if int(i[2], 0)<0:
            imm=bin(int(math.pow(2,20))+int(i[2], 0)).lstrip('0b').zfill(20)
        else:
            imm=bin(int(i[2], 0)).lstrip('0b').zfill(20)
        print '_'.join([imm, rd, '0110111'])
        instr_o=''.join([imm, rd, '0110111'])

# compressed instructions
# imm[4:2] = imm[highest_bit-4:highest_bit-2+1]

    if i[0][0:2] == 'c.' and i[-1][0] != '#':
        instr_o = bin(int(i[-1], 16)).lstrip('0b').zfill(16).ljust(32)


    if i[0][2:] == 'j':
        imm = bin(int(i[1])).lstrip('0b').zfill(12)
        instr_o = ''.join(
            ['101', imm[0], imm[7], imm[2:4], imm[1], imm[5], imm[4], imm[8:11], imm[6], '01']
        ).ljust(32)

    if i[0][2:] == 'beqz':
        rs1 = bin(int(i[1])-8).lstrip('0b').zfill(3)
        imm = bin(int(i[2])).lstrip('0b').zfill(9)
        instr_o = ''.join(
            ['110', imm[-9], imm[-5:-3], rs1, imm[-8:-6], imm[-3:-1], imm[-6], '01']
        ).ljust(32)

    if i[0][2:] == 'bnez':
        rs1 = bin(int(i[1])-8).lstrip('0b').zfill(3)
        imm = bin(int(i[2])).lstrip('0b').zfill(9)
        instr_o = ''.join(
            ['111', imm[-9], imm[-5:-3], rs1, imm[-8:-6], imm[-3:-1], imm[-6], '01']
        ).ljust(32)

    if i[0][2:] == 'jal':
        imm = bin(int(i[1])).lstrip('0b').zfill(12)
        instr_o = ''.join(
            ['001', imm[0], imm[7], imm[2:4], imm[1], imm[5], imm[4], imm[8:11], imm[6], '01']
        ).ljust(32)

    '''
    if i[0][2:] == 'lw' and int(i[2]) == 2:
        # lwsp
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        imm = bin(int(i[3])).lstrip('0b').zfill(8)
        instr_o = ''.join(
            ['010', imm[-6], '10', rd, imm[-5:-2], imm[-8:-6], '10']
        ).ljust(32)

    if i[0][2:] == 'sw' and int(i[2]) == 2:
        # swsp
        rs2 = bin(int(i[1])).lstrip('0b').zfill(5)
        imm = bin(int(i[3])).lstrip('0b').zfill(8)
        instr_o = ''.join(
            ['110', imm[-6:-2], imm[-8:-6], rs2, '10']
        ).ljust(32)

    if i[0][2:] == 'addi4spn':
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        nzuimm = bin(int(i[2])).lstrip('0b').zfill(10)
        # [::-1] to reverse a string
        instr_o = '_'.join(
            ['000', nzuimm[4:6], nzuimm[0:4], nzuimm[7], nzuimm[6], rd, '00']
        )

    if i[0][2:] == 'lw':
        # 0 is not a legal imm
        # imm are scaled by 4 -> offset[7:3] truncates right 0 of imm
        # since imm is always 4's multiple.
        rs1 = bin(int(i[2])-8).lstrip('0b').zfill(3)
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        uimm = bin(int(i[3])).lstrip('0b').zfill(8)
        instr_o = '_'.join(
            ['010', uimm[2:5], rs1, uimm[0:2], rd, '00']
        )

    if i[0][2:] == 'sw':
        rs1 = bin(int(i[2])-8).lstrip('0b').zfill(3)
        rs2 = bin(int(i[1])-8).lstrip('0b').zfill(3)
        uimm = bin(int(i[3])).lstrip('0b').zfill(8)
        instr_o = '_'.join(
            ['110', uimm[2:5], rs1, uimm[0:2], rs2, '00']
        )

    if i[0][2:] == 'addi':
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        imm = bin(int(i[2])).lstrip('0b').zfill(6)
        instr_o = '_'.join(
            ['000', imm[0], rd, imm[1:], '01']
        )

    if i[0][2:] == 'li':
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        imm = bin(int(i[2])).lstrip('0b').zfill(6)
        instr_o = '_'.join(
            ['010', imm[-6], rd, imm[-5:], '01']
        )

    if i[0][2:] == 'lui':
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        imm = bin(int(i[2])).lstrip('0b').zfill(18)
        instr_o = '_'.join(
            ['011', imm[-18], rd, imm[-17:-12], '01']
        )

    if i[0][2:] == 'srli':
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        imm = bin(int(i[2])).lstrip('0b').zfill(6)
        instr_o = '_'.join(
            ['100', imm[-6], '00', rd, imm[-5:], '01']
        )

    if i[0][2:] == 'srai':
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        imm = bin(int(i[2])).lstrip('0b').zfill(6)
        instr_o = '_'.join(
            ['100', imm[-6], '01', rd, imm[-5:], '01']
        )

    if i[0][2:] == 'andi':
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        imm = bin(int(i[2])).lstrip('0b').zfill(6)
        instr_o = '_'.join(
            ['100', imm[-6], '10', rd, imm[-5:], '01']
        )

    if i[0][2:] == 'sub':
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        rs2 = bin(int(i[2])-8).lstrip('0b').zfill(3)
        instr_o = '_'.join(
            ['100', '0', '11', rd, '00', rs2, '01']
        )

    if i[0][2:] == 'xor':
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        rs2 = bin(int(i[2])-8).lstrip('0b').zfill(3)
        instr_o = '_'.join(
            ['100', '0', '11', rd, '01', rs2, '01']
        )

    if i[0][2:] == 'or':
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        rs2 = bin(int(i[2])-8).lstrip('0b').zfill(3)
        instr_o = '_'.join(
            ['100', '0', '11', rd, '10', rs2, '01']
        )

    if i[0][2:] == 'and':
        rd = bin(int(i[1])-8).lstrip('0b').zfill(3)
        rs2 = bin(int(i[2])-8).lstrip('0b').zfill(3)
        instr_o = '_'.join(
            ['100', '0', '11', rd, '11', rs2, '01']
        )

    if i[0][2:] == 'slli':
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        imm = bin(int(i[2])).lstrip('0b').zfill(6)
        instr_o = '_'.join(
            ['000', imm[-6], rd, imm[-5:], '10']
        )

    if i[0][2:] == 'jr':
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        instr_o = '_'.join(
            ['100', '0', rd, '00000_10']
        )

    if i[0][2:] == 'mv':
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        rs2 = bin(int(i[2])).lstrip('0b').zfill(5)
        instr_o = '_'.join(
            ['100', '0', rd, rs2, '10']
        )

    if i[0][2:] == 'jalr':
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        instr_o = '_'.join(
            ['100', '1', rd, '00000_10']
        )

    if i[0][2:] == 'add':
        rd = bin(int(i[1])).lstrip('0b').zfill(5)
        rs2 = bin(int(i[2])).lstrip('0b').zfill(5)
        instr_o = '_'.join(
            ['100', '1', rd, rs2, '10']
        )
    '''

    print>>fw, instr_o+'   //  '+instr,
