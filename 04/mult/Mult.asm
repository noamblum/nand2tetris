// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

// Psuedocode for mult x * y:
// mask = 1
// for i = 0 to 15:
//    tmp = mask & y (checking bit is active)
//    if tmp != 0:
//       sum += x
//    x = x + x
//    mask = mask + mask
// return sum

@i
M=0;

@mask
M=1;

// Copy first variable
@R0
D=M;
@x
M=D;

// Make sure R2 starts as 0
@R2
M=0;

(LOOP)
    @mask
    D = M;
    @R1
    D = M & D;

    // Check mask != 0
    @LOOP_UPDATE
    D;JEQ

    @x
    D = M;

    @R2
    M = M + D;

(LOOP_UPDATE)
    @x
    D = M;
    M = M + D;

    @mask
    D = M;
    M = M + D;

@15 // Max iteration
D=A;
@i
D = M - D;
@END
D;JEQ
@i
M = M + 1;
@LOOP
0;JMP

(END)
    @END
    0;JMP