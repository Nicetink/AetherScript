AetherScript Documentation
Welcome to the official documentation for AetherScript, a modern programming language designed for simplicity, safety, and performance.

Introduction
AetherScript is a beginner-friendly language with a clean, Python-like syntax. In its current version, it supports variables, arithmetic operations, and console output, making it perfect for learning and building simple programs like calculators or data processing scripts.

Installation
Step 1: Download AetherScript IDE
Download the AetherScript IDE from the official website. The IDE requires Python 3.8+ and PyQt6.

pip install PyQt6
Step 2: Run the IDE
Save the IDE as aetheride.py and run it using Python:

python aetheride.py
Step 3: Create a File
In the IDE, click "New" to start coding. Save your files with the .aether extension.

Syntax
AetherScript’s syntax is designed to be intuitive. Here are the key features in the current version:

1. Variables
Declare variables using the let keyword.

let x = 10;
let name = "Alice";
2. Arithmetic Operations
Supported operators: +, -, *, /.

let a = 5;
let b = 3;
let sum = a + b; // 8
3. Console Output
Use print to display values.

print("Hello, AetherScript!");
print(42);
4. Comments
Single-line comments start with //.

// This is a comment
let x = 10; // Variable declaration
Example: Simple Calculator
Below is an example of a program that performs basic arithmetic operations:

// Simple calculator on AetherScript
let a = 10;           // First number
let b = 5;            // Second number

// Operations
let sum = a + b;      // Addition
let diff = a - b;     // Subtraction
let prod = a * b;     // Multiplication
let div = a / b;      // Division

// Output results
print("Sum: ");
print(sum);           // 15
print("Difference: ");
print(diff);          // 5
print("Product: ");
print(prod);          // 50
print("Division: ");
print(div);           // 2
Run it: Copy this code into AetherScript IDE, click "Run" (▶), and see the results in the output panel.

Limitations
The current version of AetherScript:

Supports only integers, floating-point numbers, strings, and basic arithmetic.
Does not include loops, conditionals (if), functions, or user input.
Runs only within AetherScript IDE.
Future Features
We plan to add:

Conditionals (if, else).
Loops (for, while).
Functions (fn).
Keyboard input.
Support for structs and modules.
Debugging
If your program fails, check:

All statements end with ;.
Variables are declared before use.
Errors appear in the IDE’s output panel, e.g.:

let x = y; // Error: Undefined variable: y
Resources
Community: Join discussions on GitHub and Discord.
Source Code: Available on GitHub.
Feedback: Reach out via email or Discord.
