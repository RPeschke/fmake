from fmake.vhdl_programm_list import add_program

from fmake.vhdl_programm_list import get_function,  print_list_of_programs

def get_help_wrap(x):
    print("Fmake is a build system for VHDL projects.")
    print("It helps to manage dependencies, compile VHDL files, and automate the build process.")
    print("\n\nFmake Programs:")
    
    print_list_of_programs(printer= print)
    
    print("to get started use 'fmake make-build' to create a build folder")
    




add_program("get-help", get_help_wrap)   
