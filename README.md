# Assembly-cleanup

This project aims to extract essential information from a raw assembly file for our RISC-V implementation project.

A raw assembly is obtained by executing a GCC compiler from GNU RISC toolchain to process an ordinary C/C++ file. Usually, there will be other blocks in the raw output. This project uses several Python scripts to extract necessary information from the ```<main>``` block, and translate that into machine code.

```
extract.py <input file> <output file>
assembly.py <input file> <output file>
mcode_gen.py <input file> <output file>
```

Under the folder "insertion sort", we start from "Insertion sort raw" the raw assembly file made by ```objdump```. Another raw assembly file "Insertion sort raw compressed" exists, which is made for RV32C. We use ```extract.py``` to extrct necessary information from "Insertion sort raw" and put it into "assembly_raw.txt". ```assembly.py``` then processed "assembly_raw.txt" and produces "assembly.txt", which is later modified manually to meet some special cases. Finally, ```mcode_gen.py``` translates the assembly file into pure machine code "instructions.txt". Files for RV32C receive a "\_c" suffix.
