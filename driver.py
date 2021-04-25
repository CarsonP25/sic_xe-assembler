#TITLE: SIC/XE Assembler
#PURPOSE: Given an SIC/XE assembly program, create object code and file. 
#AUTHOR: Carson Panduku 
#DATE OF CREATION: March 24, 2021

#import
from assembler import Assembler


def open_file(filename):
    """Open files given by the user."""

    #open the file
    try:
        with open(filename) as file_obj:
            content = file_obj.readlines()         
    #if file not found
    except FileNotFoundError:
        print("File not found. Please make sure filepath is correct.")
    file_obj.close()

    print("Beginning assembly process.")
    a.assemble(content)
    print("Assembly complete.")
    a.reset()


def show_commands(self):
    """lists commands upon user request"""
    print('-h\t--lists all commands')
    print('-o filename\t--opens file for assembling')
    print('-q\t--terminates program')


#init assembler
a = Assembler()

#greet user
print("***-------SIC/XE Assembler Ver. 0.5-------***")
print("Welcome! Please enter you command.",
    "(type '-h' for a list of commands)")

#run code based on command entered
while True:
    command = input()
        
    #quit
    if command == '-q':
        break

    #open file
    elif command[0:2] == '-o':
        if '.txt' in command[3:]:
            open_file(command[3:])
            print("Done!")
                
    #print all commands
    elif command[0:2] == '-h':
        show_commands()

    #invalid input
    else:
        print(f"{command} is not a supported command")



