// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// Pseudo code:
// key = getInput()
// if key == 0:
//      fillValue = 0
// else:
//      fillValue = -1
// for all screen:
//   set to fillValue
// goto start

(MAIN_LOOP)
    @KBD
    D=M;

    @BLACK
    D;JNE
(WHITE)
    @fillValue
    M=0;
    @CHECK_MATCH
    0;JMP

(BLACK)
    @fillValue
    M=-1;

(CHECK_MATCH) // Checks if the top-right pixel is filled with the correct value
    @fillValue
    D=M;
    @SCREEN
    D = M-D;
    @DRAW_LOOP_START
    D;JNE
    @MAIN_LOOP
    0;JMP


(DRAW_LOOP_START)
    @SCREEN
    D=A;
    @curInd
    M=D;
(DRAW_LOOP)
    @fillValue
    D=M;
    @curInd
    A=M;
    M=D;

    // Go to next pixel
    D=A + 1;
    @curInd
    M=D;

    // Check stop iteration
    @KBD
    D = D - A;
    @DRAW_LOOP
    D;JNE

@MAIN_LOOP
0;JMP
    