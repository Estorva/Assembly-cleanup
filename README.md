# Assembly-cleanup

This program aims to extract essential information from a raw assembly file for our RISC-V implementation project.

A raw assembly is obtained by executing a GCC compiler from GNU RISC toolchain to process an ordinary C/C++ file. Usually, there will be other blocks in the raw output. This program extract necessary information from the ```<main>``` block.
