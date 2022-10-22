// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Initialize variables
// i = 0
@0
D=A
@i
M=D

// maxAddr = R14 & minAddr = R14
@R14
D=M
@maxAddr
M=D
@minAddr
M=D


(LOOP)
    @i
    D=M
    @R15
    D = D-M
    @LOOP_END
    D;JEQ
        // Access the i-th element in the array
        @i
        D=M
        @R14
        A=M+D
        D=M
        // Check Array[i] >= max
        @maxAddr
        A=M
        D=D-M
        
        // If Array[i] < max, skip updating it
        @UPDATE_MIN
        D;JLT
        // D = *R14 + i
        @R14
        D=M
        @i
        D=D+M
        @maxAddr
        M=D

        (UPDATE_MIN)
        // Access the i-th element in the array
        @i
        D=M
        @R14
        A=M+D
        D=M
        // Check Array[i] <= min
        @minAddr
        A=M
        D=M-D

        // If Array[i] > min, skip updating it
        @LOOP_UPDATE
        D;JLT
        // D = *R14 + i
        @R14
        D=M
        @i
        D=D+M
        @minAddr
        M=D



    (LOOP_UPDATE)
    // i++
    @i
    M=M+1

    @LOOP
    0;JMP
(LOOP_END)


// Swap
// tmp = *maxAddr
@maxAddr
A=M
D=M
@tmp
M=D

// *maxAddr = *minAddr
@minAddr
A=M
D=M
@maxAddr
A=M
M=D

// *minAddr = tmp
@tmp
D=M
@minAddr
A=M
M=D


(END_PROGRAM)
@END_PROGRAM
0;JMP

